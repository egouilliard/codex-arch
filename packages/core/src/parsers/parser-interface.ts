/**
 * Represents a single entity node in the code graph
 */
export interface CodeEntity {
  id: string;
  type: CodeEntityType;
  name: string;
  filePath: string;
  location: CodeLocation;
  properties: Record<string, any>;
}

/**
 * Types of code entities that can be recognized
 */
export enum CodeEntityType {
  File = 'File',
  Function = 'Function',
  Class = 'Class',
  Interface = 'Interface',
  Type = 'Type',
  Variable = 'Variable',
  Method = 'Method',
  Property = 'Property',
  Module = 'Module',
  Namespace = 'Namespace',
  Parameter = 'Parameter'
}

/**
 * Represents a relationship between code entities
 */
export interface CodeRelationship {
  source: string; // Source entity ID
  target: string; // Target entity ID
  type: CodeRelationshipType;
  properties: Record<string, any>;
}

/**
 * Types of relationships between code entities
 */
export enum CodeRelationshipType {
  Imports = 'IMPORTS',
  Extends = 'EXTENDS',
  Implements = 'IMPLEMENTS',
  Contains = 'CONTAINS',
  References = 'REFERENCES',
  Calls = 'CALLS',
  Returns = 'RETURNS',
  Declares = 'DECLARES',
  DependsOn = 'DEPENDS_ON'
}

/**
 * Represents the location of a code entity in a file
 */
export interface CodeLocation {
  startLine: number;
  startColumn: number;
  endLine: number;
  endColumn: number;
}

/**
 * Interface that all language parsers must implement
 */
export interface Parser {
  /**
   * Parse a single file
   * @param filePath Path to the file to parse
   * @returns Parsed code entities and relationships
   */
  parseFile(filePath: string): Promise<{
    entities: CodeEntity[];
    relationships: CodeRelationship[];
  }>;

  /**
   * Parse a directory of files
   * @param dirPath Path to the directory to parse
   * @param options Parsing options
   * @returns Parsed code entities and relationships
   */
  parseDirectory(
    dirPath: string,
    options?: {
      exclude?: string[];
      include?: string[];
      recursive?: boolean;
    }
  ): Promise<{
    entities: CodeEntity[];
    relationships: CodeRelationship[];
  }>;
} 