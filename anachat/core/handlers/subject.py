"""This module defines the subject state and the subject handler"""
import json
import uuid
from lunr import lunr
from lunr.exceptions import QueryParseError

from ..pagination import pagination
from ..resources import data
from ..states.utils import create_panel_state, create_reply_state, create_state_loader
from ..states.utils import statemanager
from .action import ActionHandler
from .utils import HandlerWithPaths


def subject_name(subject, key=None):
    """Return subject name"""
    if key:
        return key.rsplit(" > ", 2)[-1]
    name = subject['name']
    if isinstance(name, list):
        return name[0]
    return name


def create_subject_state(subject, key=None):
    """Creates state for subject"""
    name = subject_name(subject, key)
    if not key:
        key = str(uuid.uuid4())
        parent_key = str(uuid.uuid4())
    else:
        parent_key = key.rsplit(" > ", 2)[0]
    @statemanager()
    def subject_state(comm):
        options = []
        if 'description' in subject:
            options.append({
                'key': f"{key}::description",
                'label': 'Description',
                'state': create_reply_state(subject['description']),
            })
        if 'url' in subject:
            options.append({
                'key': f"{key}::url",
                'label': 'Panel',
                'state': create_panel_state(subject['url'], name),
            })
        if 'parent' in subject:
            options.append({
                'key': parent_key,
                'label': 'Parent',
                'state': create_subject_state(subject['parent'], parent_key)
            })
        if 'actions' in subject:
            actions = [{
                'key': action['state'],
                'label': action['name'],
                'state': create_state_loader(action['state'])
            } for action in subject['actions']]
            options.append({
                'key': f"{key}::actions",
                'label': 'Actions',
                'state': create_state_list(name, actions, "action(s)")
            })
        if 'children' in subject:
            children = []
            for child in subject['children']:
                child_name = subject_name(child)
                child_key = key + " > " + child_name
                children.append({
                    'key': child_key,
                    'label': child_name,
                    'state': create_subject_state(child, child_key)
                })
            options.append({
                'key': f"{key}::children",
                'label': 'Children',
                'state': create_state_list(name, children, "child subject(s)")
            })

        if not options:
            comm.reply(f"Unfortunately, there is nothing in my knowlegde base about {name}.")
        else:
            comm.reply(f"What do you want to know about {name}?")
            ActionHandler().show_options(comm, options)
    return subject_state


def create_state_list(name, children, theme):
    """Creates state for list of children of subject"""
    @statemanager()
    def children_state(comm):
        comm.reply(f"{name} has {len(children)} {theme}. Please select one:")
        pagination(comm, children)
    return children_state


class SubjectHandler(HandlerWithPaths):
    """Provides functions for searching a subject"""

    def __init__(self):
        self.docmap = {}
        self.idx = None
        super().__init__()

    def build_document_list(self, forest):
        """Builds document list to use lurn for searching"""
        docmap = {}
        documents = []

        visit = [('', tree) for tree in forest]
        while visit:
            current = visit.pop()
            if 'redirect' in current[1]:
                filepath = data() / current[1]['redirect']
                del current[1]['redirect']
                with open(filepath, 'r', encoding='utf-8') as subfile:
                    subvisit = [(current[0], {**tree, **current[1]}) for tree in json.load(subfile)]
                    visit = visit + subvisit
                    print(subvisit)
                self.paths[filepath] = self.getmtime(filepath)
                continue
            names = current[1]['name']
            if isinstance(names, str):
                names = [names]
            for name in names:
                key = name
                if current[0]:
                    key = current[0] + ' > ' + key
                document = {
                    'key': key,
                    'name': name,
                    'description': current[1].get('description', ''),
                    'keywords': current[1].get('keywords', ''),
                    'node': current[1],
                }
                documents.append(document)
                docmap[key] = document
                for child in current[1].get('children', []):
                    child['parent'] = current[1]
                    visit.append((key, child))
        return docmap, documents

    def inner_reload(self):
        """Reloads lunr indexes based on subjects file"""
        filepath = data() / 'subjects.json'
        with open(filepath, 'r', encoding='utf-8') as subjects:
            forest = json.load(subjects)
        self.docmap, documents = self.build_document_list(forest)
        self.idx = lunr(ref='key', fields=(
            {'field_name': 'key', 'boost': 5},
            {'field_name': 'name', 'boost': 10},
            {'field_name': 'description', 'boost': 1},
            {'field_name': 'keywords', 'boost': 7}
        ), documents=documents)
        self.paths[filepath] = self.getmtime(filepath)

    def inner_process_message(self, comm, text):
        """Processes users message"""
        matches = list(self.search(text))
        if matches:
            comm.reply(f"I found {len(matches)} subjects. "
                       f"Which one of these best describe your query?")
            pagination(comm, [{
                'key': match['ref'],
                'label': subject_name(node['name'], match['ref']),
                'state': create_subject_state(node, key=match['ref'])
            } for match, node in matches])
            return True
        return None

    def search(self, text):
        """Searches subject based on input text"""
        try:
            matches = self.idx.search(text)
        except QueryParseError:
            matches = []
        node_ids = set()
        for match in matches:
            node = self.docmap[match['ref']]['node']
            node_id = id(node)
            if node_id not in node_ids:
                node_ids.add(node_id)
                yield (match, node)

    def state_by_key(self, key):
        """Return subject state by key, if it exists"""
        if key in self.docmap:
            node = self.docmap[key]['node']
            return create_subject_state(node, key=key)
        return None
