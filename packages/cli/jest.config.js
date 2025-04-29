module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/tests/**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      useESM: false,
    }],
  },
  moduleNameMapper: {
    '^conf$': '<rootDir>/tests/mocks/conf.mock.js',
    '^open$': '<rootDir>/tests/mocks/open.mock.js',
  },
  transformIgnorePatterns: [
    'node_modules/(?!(conf|open)/)'
  ],
  moduleDirectories: ['node_modules', 'src'],
}; 