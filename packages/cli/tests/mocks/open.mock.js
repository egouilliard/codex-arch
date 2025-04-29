/**
 * Mock implementation of the open package for testing
 */
function openMock(target, options) {
  return Promise.resolve({
    pid: 12345,
    command: 'mock-command',
    arguments: [target],
  });
}

// Add the same API as the real 'open' package
openMock.openApp = (name, options) => openMock(`app:${name}`, options);
openMock.openSync = (target, options) => ({ pid: 12345 });

module.exports = openMock; 