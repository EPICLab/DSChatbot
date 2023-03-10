"""This module defines the subject state and the subject handler"""
from __future__ import annotations
from typing import TYPE_CHECKING
import json
import uuid

from lunr import lunr  # type: ignore
from lunr.exceptions import QueryParseError  # type: ignore

from ..pagination import pagination
from ..resources import data
from ..states.utils import create_panel_state, create_reply_state, create_state_loader
from ..states.utils import statemanager
from ..action import show_options
from .utils import HandlerWithPaths


if TYPE_CHECKING:
    from typing import List, Optional, TypedDict
    from ....comm.message import MessageContext
    from ..states.state import StateCallable, StateDefinition
    from ..action import StatefulOption


    class Action(TypedDict, total=False):
        """Defines an Action"""
        name: str
        state: str


    class Subject(TypedDict, total=False):
        """Defines a Subject"""
        name: str | List[str]
        description: Optional[str]
        url: Optional[str]
        parent: Optional[Subject]
        actions: Optional[List[Action]]
        children: Optional[List[Subject]]


def subject_name(subject: Subject, key: str | None=None) -> str:
    """Return subject name"""
    if key:
        return key.rsplit(" > ", 1)[-1]
    name = subject['name']
    if isinstance(name, list):
        return name[0]
    return name


def create_subject_state(subject: Subject, key: str | None=None) -> StateCallable:
    """Creates state for subject"""
    name = subject_name(subject, key)
    if not key:
        key = str(uuid.uuid4())
        parent_key = str(uuid.uuid4())
    else:
        parent_key = key.rsplit(" > ", 1)[0]
    @statemanager()
    def subject_state(context: MessageContext):
        options: List[StatefulOption] = []
        if 'description' in subject:
            options.append({
                'key': f"{key}::description",
                'label': 'Description',
                'state': create_reply_state(subject['description']),
            })
        if 'url' in subject:
            options.append({
                'key': f"{key}::url",
                'label': 'Documentation',
                'state': create_panel_state(subject['url'], name),
            })
        if subject_parent := subject.get('parent', None):
            parent_name = subject_name(subject_parent)
            options.append({
                'key': parent_key,
                'label': f'⬆️ {parent_name}',
                'state': create_subject_state(subject_parent, parent_key)
            })
        if subject_actions := subject.get('actions', []):
            actions: List[StatefulOption] = [{
                'key': action['state'],
                'label': action['name'],
                'state': create_state_loader(action['state'])
            } for action in subject_actions]
            options.append({
                'key': f"{key}::actions",
                'label': 'Actions',
                'state': create_state_list(name, actions, "action(s)")
            })
        if subject_children := subject.get('children', []):
            children: List[StatefulOption] = []
            children_names = []
            for child in subject_children:
                child_name = subject_name(child)
                children_names.append(child_name)
                child_key = f"{key} > {child_name}"
                children.append({
                    'key': child_key,
                    'label': child_name,
                    'state': create_subject_state(child, child_key)
                })
            options.append({
                'key': f"{key}::children",
                'label': f'⬇️ {", ".join(children_names)}',
                'state': create_state_list(name, children, "child subject(s)")
            })

        if not options:
            context.reply(
                f"Unfortunately, there is nothing in my knowlegde base about {name}.",
                checkpoint=subject_state
            )
        else:
            show_options(context, options, text=f"What do you want to know about {name}?")
    return subject_state


def create_state_list(name: str, children: List[StatefulOption], theme: str) -> StateCallable:
    """Creates state for list of children of subject"""
    @statemanager()
    def children_state(context: MessageContext) -> StateDefinition:
        text = f"{name} has {len(children)} {theme}. Please select one:"
        pagination(context, children, text=text)
        return None
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

    def inner_reload(self) -> None:
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

    def inner_process_message(self, context: MessageContext) -> StateDefinition:
        """Processes users message"""
        matches = list(self.search(context.text))
        if matches:
            text = (f"I found {len(matches)} subjects. "
                    f"Which one of these best describe your query?")
            pagination(context, [{
                'key': match['ref'],
                'label': subject_name(node['name'], match['ref']),
                'state': create_subject_state(node, key=match['ref'])
            } for match, node in matches], text=text)
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

    def state_by_key(self, key) -> StateDefinition:
        """Return subject state by key, if it exists"""
        if key in self.docmap:
            node = self.docmap[key]['node']
            return create_subject_state(node, key=key)
        return None
