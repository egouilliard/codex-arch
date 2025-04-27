import * as ts from 'typescript';
import * as path from 'path';
import * as fs from 'fs/promises';
import { glob } from 'glob';
import {
  CodeEntity,
  CodeEntityType,
  CodeLocation,
  CodeRelationship,
  CodeRelationshipType,
  Parser
} from '@codex-arch/core';

/**
 * Implementation of the Parser interface for TypeScript code
 */
export class TypeScriptParser implements Parser {
  private sourceFiles: Map<string, ts.SourceFile> = new Map();
  private entities: Map<string, CodeEntity> = new Map();
  private relationships: CodeRelationship[] = [];
  private program: ts.Program | null = null;

  /**
   * Parse a single TypeScript file
   */
  public async parseFile(filePath: string): Promise<{
    entities: CodeEntity[];
    relationships: CodeRelationship[];
  }> {
    // Reset collections
    this.entities = new Map();
    this.relationships = [];
    this.sourceFiles = new Map();

    // Create a program for the single file
    const content = await fs.readFile(filePath, 'utf-8');
    const sourceFile = ts.createSourceFile(
      filePath,
      content,
      ts.ScriptTarget.Latest,
      true
    );
    
    this.sourceFiles.set(filePath, sourceFile);
    
    // Process the source file
    this.processSourceFile(sourceFile);
    
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
  ): Promise<{
    entities: CodeEntity[];
    relationships: CodeRelationship[];
  }> {
    // Reset collections
    this.entities = new Map();
    this.relationships = [];
    this.sourceFiles = new Map();

    const globPattern = options?.recursive !== false
      ? path.join(dirPath, '**/*.{ts,tsx}')
      : path.join(dirPath, '*.{ts,tsx}');
    
    const excludePatterns = options?.exclude || [];
    const includePatterns = options?.include || ['**/*.ts', '**/*.tsx'];
    
    // Find all TypeScript files
    const files = await glob(globPattern, {
      ignore: excludePatterns
    });
    
    // Create a program for all files
    const compilerOptions = {
      target: ts.ScriptTarget.Latest,
      module: ts.ModuleKind.CommonJS
    };
    
    this.program = ts.createProgram(files, compilerOptions);
    
    // Process each source file
    for (const sourceFile of this.program.getSourceFiles()) {
      if (!sourceFile.isDeclarationFile) {
        this.sourceFiles.set(sourceFile.fileName, sourceFile);
        this.processSourceFile(sourceFile);
      }
    }
    
    return {
      entities: Array.from(this.entities.values()),
      relationships: this.relationships
    };
  }

  /**
   * Process a TypeScript source file to extract entities and relationships
   */
  private processSourceFile(sourceFile: ts.SourceFile): void {
    const filePath = sourceFile.fileName;
    
    // Create a file entity
    const fileId = this.createId(filePath, 'file');
    const fileEntity: CodeEntity = {
      id: fileId,
      type: CodeEntityType.File,
      name: path.basename(filePath),
      filePath,
      location: {
        startLine: 1,
        startColumn: 1,
        endLine: sourceFile.getLineAndCharacterOfPosition(sourceFile.getEnd()).line + 1,
        endColumn: sourceFile.getLineAndCharacterOfPosition(sourceFile.getEnd()).character + 1
      },
      properties: {
        ext: path.extname(filePath)
      }
    };
    
    this.entities.set(fileId, fileEntity);
    
    // Visit all nodes in the file
    ts.forEachChild(sourceFile, (node) => {
      this.visitNode(node, fileId, sourceFile);
    });
  }

  /**
   * Visit a TypeScript AST node and extract entities/relationships
   */
  private visitNode(node: ts.Node, parentId: string, sourceFile: ts.SourceFile): void {
    // Placeholder implementation - in a real implementation,
    // this would extract various entity types and relationships
    
    // Example: Extract classes
    if (ts.isClassDeclaration(node) && node.name) {
      const name = node.name.getText();
      const location = this.getNodeLocation(node, sourceFile);
      const id = this.createId(sourceFile.fileName, 'class', name);
      
      // Create the class entity
      const classEntity: CodeEntity = {
        id,
        type: CodeEntityType.Class,
        name,
        filePath: sourceFile.fileName,
        location,
        properties: {
          isExported: this.hasExportModifier(node)
        }
      };
      
      this.entities.set(id, classEntity);
      
      // Create a CONTAINS relationship from the file to the class
      this.relationships.push({
        source: parentId,
        target: id,
        type: CodeRelationshipType.Contains,
        properties: {}
      });
      
      // Process class members
      node.members.forEach(member => {
        this.visitNode(member, id, sourceFile);
      });
    }
    
    // Recursively visit children
    node.forEachChild(child => this.visitNode(child, parentId, sourceFile));
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
  private hasExportModifier(node: ts.Node): boolean {
    if (!node.modifiers) {
      return false;
    }
    
    return node.modifiers.some(
      modifier => modifier.kind === ts.SyntaxKind.ExportKeyword
    );
  }

  /**
   * Create a unique ID for an entity
   */
  private createId(filePath: string, type: string, name?: string): string {
    const base = `${filePath}:${type}`;
    return name ? `${base}:${name}` : base;
  }
} 