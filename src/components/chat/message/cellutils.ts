import type { ISessionContext } from '@jupyterlab/apputils';
import {
  CodeCell,
  Cell,
  RawCell,
  CodeCellModel,
  type IRawCellModel,
  RawCellModel,
  type ICodeCellModel,
  CellModel
} from '@jupyterlab/cells';
import type { Kernel, KernelMessage } from '@jupyterlab/services';

export interface IContentFactory extends Cell.IContentFactory {
  /**
   * Create a new code cell widget.
   */
  createCodeCell(options: CodeCell.IOptions): CodeCell;

  /**
   * Create a new raw cell widget.
   */
  createRawCell(options: RawCell.IOptions): RawCell;
}

export class ContentFactory
  extends Cell.ContentFactory
  implements IContentFactory
{
  /**
   * Create a new code cell widget.
   *
   * #### Notes
   * If no cell content factory is passed in with the options, the one on the
   * notebook content factory is used.
   */
  createCodeCell(options: CodeCell.IOptions): CodeCell {
    if (!options.contentFactory) {
      options.contentFactory = this;
    }
    return new CodeCell(options).initializeState();
  }

  /**
   * Create a new raw cell widget.
   *
   * #### Notes
   * If no cell content factory is passed in with the options, the one on the
   * notebook content factory is used.
   */
  createRawCell(options: RawCell.IOptions): RawCell {
    if (!options.contentFactory) {
      options.contentFactory = this;
    }
    return new RawCell(options).initializeState();
  }
}

/**
 * The default implementation of an `IModelFactory`.
 */
export class ModelFactory {
  /**
   * Create a new cell model factory.
   */
  constructor(options: IModelFactoryOptions = {}) {
    this.codeCellContentFactory =
      options.codeCellContentFactory || CodeCellModel.defaultContentFactory;
  }

  /**
   * The factory for output area models.
   */
  readonly codeCellContentFactory: CodeCellModel.IContentFactory;

  /**
   * Create a new code cell.
   *
   * @param source - The data to use for the original source data.
   *
   * @returns A new code cell. If a source cell is provided, the
   *   new cell will be initialized with the data from the source.
   *   If the contentFactory is not provided, the instance
   *   `codeCellContentFactory` will be used.
   */
  createCodeCell(options: CodeCellModel.IOptions): ICodeCellModel {
    if (!options.contentFactory) {
      options.contentFactory = this.codeCellContentFactory;
    }
    return new CodeCellModel(options);
  }

  /**
   * Create a new raw cell.
   *
   * @param source - The data to use for the original source data.
   *
   * @returns A new raw cell. If a source cell is provided, the
   *   new cell will be initialized with the data from the source.
   */
  createRawCell(options: CellModel.IOptions): IRawCellModel {
    return new RawCellModel(options);
  }
}

/**
 * The options used to initialize a `ModelFactory`.
 */
export interface IModelFactoryOptions {
  /**
   * The factory for output area models.
   */
  codeCellContentFactory?: CodeCellModel.IContentFactory;
}


export async function execute_cell(
  cell: CodeCell,
  sessionContext: ISessionContext,
): Promise<KernelMessage.IExecuteReplyMsg | void> {
  const model = cell.model;
  const code = model.sharedModel.getSource();
  if (!code.trim() || !sessionContext.session?.kernel) {
    model.sharedModel.transact(() => {
      model.clearExecution();
    });
    return;
  }
  const cellId = { cellId: model.sharedModel.getId() };

  model.sharedModel.transact(() => {
    model.clearExecution();
    cell.outputHidden = false;
  });
  cell.setPrompt('*');
  model.trusted = true;
  let future:
    | Kernel.IFuture<
        KernelMessage.IExecuteRequestMsg,
        KernelMessage.IExecuteReplyMsg
      >
    | undefined;
  try {
    const content: KernelMessage.IExecuteRequestMsg['content'] = {
      code,
      stop_on_error: true,
      store_history: false,
      silent: false
    };
    const kernel = sessionContext.session?.kernel;
    if (!kernel) {
      throw new Error('Session has no kernel.');
    }
    const future = kernel.requestExecute(content, false, { ...model.metadata, ...cellId } as any);
    cell.outputArea.future = future;

    const msgPromise = future.done;
    // cell.outputArea.future assigned synchronously in `execute`
    // model.deleteMetadata('execution');
    // Save this execution's future so we can compare in the catch below.
    const msg = (await msgPromise)!;
    model.executionCount = msg.content.execution_count;
    return msg;
  } catch (e) {
    // If we started executing, and the cell is still indicating this
    // execution, clear the prompt.
    if (future && !cell.isDisposed && cell.outputArea.future === future) {
      cell.setPrompt('');
    }
    throw e;
  }
}

