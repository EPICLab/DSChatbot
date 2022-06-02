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
