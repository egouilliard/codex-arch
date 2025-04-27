import * as ts from 'typescript';
import * as path from 'path';
import * as fs from 'fs/promises';
import * as fsSync from 'fs';
import { glob } from 'glob';
import {
  CodeEntity,
  CodeEntityType,
  CodeLocation,
  CodeRelationship,
  CodeRelationshipType,
  Parser,
  ImportType
} from '@codex-arch/core';

/**
 * Information about an import statement
 */
interface ImportInfo {
  path: string;
  type: ImportType;
  names?: string[];
  alias?: string;
}

/**
 * Result of parsing a file
 */
interface ParseResult {
  entities: CodeEntity[];
  relationships: CodeRelationship[];
}

/**
 * Implementation of the Parser interface for TypeScript code
 */
export class TypeScriptParser implements Parser {
  private sourceFiles: Map<string, ts.SourceFile> = new Map();
  private entities: Map<string, CodeEntity> = new Map();
  private relationships: CodeRelationship[] = [];
  private program: ts.Program | null = null;
  private basePath: string = '';

  /**
   * Parse a single TypeScript file
   */
  public async parseFile(filePath: string): Promise<ParseResult> {
    // Reset collections
    this.entities = new Map();
    this.relationships = [];
    this.sourceFiles = new Map();
    
    // Set basePath to directory containing the file
    this.basePath = path.dirname(filePath);
    
    // Find workspace root by looking for test-repositories directory
    const testRepoIndex = filePath.indexOf('test-repositories');
    if (testRepoIndex !== -1) {
      this.basePath = filePath.substring(0, testRepoIndex);
    }

    // Create a program for the single file
    const content = await fs.readFile(filePath, 'utf-8');
    const sourceFile = ts.createSourceFile(
      filePath,
      content,
      ts.ScriptTarget.Latest,
      true
    );
    
    this.sourceFiles.set(filePath, sourceFile);
    
    // Process the source file to create the file entity
    const fileId = this.processFileEntity(sourceFile);
    
    // Extract imports from the source file
    this.extractImports(sourceFile, fileId);
    
    return {
      entities: Array.from(this.entities.values()),
      relationships: this.relationships
    };
  }

  /**
   * Parse a directory of TypeScript files
   */
  public async parseDirectory(
    dirPath: string,
    options?: {
      exclude?: string[];
      include?: string[];
      recursive?: boolean;
    }
  ): Promise<ParseResult> {
    // Reset collections
    this.entities = new Map();
    this.relationships = [];
    this.sourceFiles = new Map();
    
    // Set basePath to the directory being parsed
    this.basePath = dirPath;
    
    // Find workspace root by looking for test-repositories directory
    const testRepoIndex = dirPath.indexOf('test-repositories');
    if (testRepoIndex !== -1) {
      this.basePath = dirPath.substring(0, testRepoIndex);
    }

    const globPattern = options?.recursive !== false
      ? path.join(dirPath, '**/*.{ts,tsx}')
      : path.join(dirPath, '*.{ts,tsx}');
    
    const excludePatterns = options?.exclude || [];
    
    // Find all TypeScript files
    const files = await glob(globPattern, {
      ignore: excludePatterns
    });
    
    // Create a program for all files
    const compilerOptions = {
      target: ts.ScriptTarget.Latest,
      module: ts.ModuleKind.CommonJS,
      baseUrl: dirPath,
      allowJs: true
    };
    
    this.program = ts.createProgram(files, compilerOptions);
    
    // Process each source file
    for (const sourceFile of this.program.getSourceFiles()) {
      if (!sourceFile.isDeclarationFile) {
        this.sourceFiles.set(sourceFile.fileName, sourceFile);
        const fileId = this.processFileEntity(sourceFile);
        this.extractImports(sourceFile, fileId);
      }
    }
    
    return {
      entities: Array.from(this.entities.values()),
      relationships: this.relationships
    };
  }

  /**
   * Process a source file to create a file entity
   */
  private processFileEntity(sourceFile: ts.SourceFile): string {
    const filePath = sourceFile.fileName;
    const normalizedPath = this.normalizeFilePath(filePath);
    
    // Create a file entity
    const fileId = this.createId(filePath, 'file');
    
    // Get file size synchronously
    let fileSize: number | undefined;
    try {
      fileSize = fsSync.statSync(filePath).size;
    } catch (error) {
      fileSize = undefined;
    }
    
    const fileEntity: CodeEntity = {
      id: fileId,
      type: CodeEntityType.File,
      name: path.basename(filePath),
      filePath: normalizedPath,
      location: {
        startLine: 1,
        startColumn: 1,
        endLine: sourceFile.getLineAndCharacterOfPosition(sourceFile.getEnd()).line + 1,
        endColumn: sourceFile.getLineAndCharacterOfPosition(sourceFile.getEnd()).character + 1
      },
      properties: {
        ext: path.extname(filePath),
        size: fileSize
      }
    };
    
    this.entities.set(fileId, fileEntity);
    return fileId;
  }

  /**
   * Extract imports from a source file
   */
  private extractImports(sourceFile: ts.SourceFile, fileId: string): void {
    ts.forEachChild(sourceFile, (node) => {
      if (ts.isImportDeclaration(node)) {
        this.processImportDeclaration(node, sourceFile, fileId);
      }
    });
  }

  /**
   * Process an import declaration and create relationships
   */
  private processImportDeclaration(
    node: ts.ImportDeclaration, 
    sourceFile: ts.SourceFile, 
    fileId: string
  ): void {
    // Get the import path
    if (!node.moduleSpecifier || !ts.isStringLiteral(node.moduleSpecifier)) {
      return;
    }
    
    const importPath = node.moduleSpecifier.text;
    const sourceFilePath = sourceFile.fileName;
    
    // Resolve the actual file path
    const resolvedPath = this.resolveImportPath(importPath, sourceFilePath);
    if (!resolvedPath) {
      return; // Skip if we can't resolve the import
    }
    
    const normalizedResolvedPath = this.normalizeFilePath(resolvedPath);
    
    // Create a file entity for the imported file if it doesn't exist
    const targetFileId = this.createId(resolvedPath, 'file');
    
    if (!this.entities.has(targetFileId)) {
      // Create a placeholder file entity
      const fileEntity: CodeEntity = {
        id: targetFileId,
        type: CodeEntityType.File,
        name: path.basename(resolvedPath),
        filePath: normalizedResolvedPath,
        location: {
          startLine: 0,
          startColumn: 0,
          endLine: 0,
          endColumn: 0
        },
        properties: {
          ext: path.extname(resolvedPath),
          isPlaceholder: true
        }
      };
      
      this.entities.set(targetFileId, fileEntity);
    }
    
    // Determine the import type
    let importType = ImportType.SideEffect; // Default for "import 'module'"
    
    if (node.importClause) {
      if (node.importClause.name) {
        importType = ImportType.Default; // import Default from 'module'
      } else if (node.importClause.namedBindings) {
        if (ts.isNamespaceImport(node.importClause.namedBindings)) {
          importType = ImportType.Namespace; // import * as Namespace from 'module'
        } else if (ts.isNamedImports(node.importClause.namedBindings)) {
          importType = ImportType.Named; // import { Named } from 'module'
        }
      }
    }
    
    // Create the relationship
    this.relationships.push({
      source: fileId,
      target: targetFileId,
      type: CodeRelationshipType.Imports,
      properties: {
        importType,
        importPath
      }
    });
  }

  /**
   * Resolve an import path to an absolute file path
   */
  private resolveImportPath(importPath: string, containingFile: string): string | null {
    // If it's a relative path, resolve it relative to the containing file
    if (importPath.startsWith('.')) {
      const dirName = path.dirname(containingFile);
      let resolvedPath = path.resolve(dirName, importPath);
      
      // Check various extensions
      const extensions = ['.ts', '.tsx', '.js', '.jsx', '.d.ts'];
      
      // First check if the exact path exists
      if (this.fileExistsSync(resolvedPath)) {
        return resolvedPath;
      }
      
      // Then check with extensions if no extension provided
      if (!path.extname(resolvedPath)) {
        for (const ext of extensions) {
          const pathWithExt = resolvedPath + ext;
          if (this.fileExistsSync(pathWithExt)) {
            return pathWithExt;
          }
          
          // Also check for index files
          const indexFile = path.join(resolvedPath, `index${ext}`);
          if (this.fileExistsSync(indexFile)) {
            return indexFile;
          }
        }
      }
      return null;
    }
    
    // For non-relative imports, we can't resolve them easily without full TS compiler context
    // This would usually involve checking node_modules or tsconfig paths
    // For now, just return null to indicate we couldn't resolve it
    return null;
  }

  /**
   * Check if a file exists
   */
  private fileExistsSync(filePath: string): boolean {
    try {
      return fsSync.statSync(filePath).isFile();
    } catch (error) {
      return false;
    }
  }

  /**
   * Get location information for a node
   */
  private getNodeLocation(node: ts.Node, sourceFile: ts.SourceFile): CodeLocation {
    const start = node.getStart(sourceFile);
    const end = node.getEnd();
    const startLineAndChar = sourceFile.getLineAndCharacterOfPosition(start);
    const endLineAndChar = sourceFile.getLineAndCharacterOfPosition(end);
    
    return {
      startLine: startLineAndChar.line + 1,
      startColumn: startLineAndChar.character + 1,
      endLine: endLineAndChar.line + 1,
      endColumn: endLineAndChar.character + 1
    };
  }

  /**
   * Check if a node has the 'export' modifier
   */
  private hasExportModifier(node: ts.HasModifiers): boolean {
    if (!node.modifiers) {
      return false;
    }
    
    return node.modifiers.some(
      (modifier) => modifier.kind === ts.SyntaxKind.ExportKeyword
    );
  }

  /**
   * Create a unique ID for an entity
   */
  private createId(filePath: string, type: string, name?: string): string {
    // Convert absolute path to relative path format
    const normalizedPath = this.normalizeFilePath(filePath);
    const base = `${normalizedPath}:${type}`;
    return name ? `${base}:${name}` : base;
  }

  /**
   * Normalize file path to a consistent relative format
   * Converts absolute paths to the same relative format used for source paths
   */
  private normalizeFilePath(filePath: string): string {
    // If it's already a relative path with the expected format, return as is
    if (filePath.startsWith('test-repositories/')) {
      return filePath;
    }
    
    // Check if it's an absolute path
    if (path.isAbsolute(filePath)) {
      // Look for 'test-repositories' directory as a marker for the relative path start
      const testRepoIndex = filePath.indexOf('test-repositories');
      if (testRepoIndex !== -1) {
        return filePath.substring(testRepoIndex);
      }
      
      // If we can't find the marker but have a basePath set
      if (this.basePath && this.basePath !== '') {
        try {
          // First, check if basePath contains 'test-repositories'
          const baseTestRepoIndex = this.basePath.indexOf('test-repositories');
          if (baseTestRepoIndex !== -1) {
            const workspaceRoot = this.basePath.substring(0, baseTestRepoIndex);
            // Get path relative to workspace root
            if (filePath.startsWith(workspaceRoot)) {
              return filePath.substring(workspaceRoot.length);
            }
          }
          
          // Otherwise, make it relative to basePath
          const relativePath = path.relative(this.basePath, filePath);
          // Avoid paths starting with .. which indicates going up from basePath
          if (!relativePath.startsWith('..')) {
            return relativePath;
          }
        } catch (error) {
          // If there's an error, continue to return the original path
        }
      }
    }
    
    // If we couldn't normalize it or it's already a non-absolute path, return as is
    return filePath;
  }
} 