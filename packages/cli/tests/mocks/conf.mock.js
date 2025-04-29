/**
 * Mock implementation of the conf package for testing
 */
class ConfMock {
  constructor(options = {}) {
    this.store = {};
    this.options = options;
  }

  get(key) {
    if (key) {
      return this.store[key];
    }
    return this.store;
  }

  set(key, value) {
    if (typeof key === 'object') {
      this.store = { ...this.store, ...key };
    } else {
      this.store[key] = value;
    }
  }

  has(key) {
    return key in this.store;
  }

  delete(key) {
    delete this.store[key];
  }

  clear() {
    this.store = {};
  }
}

module.exports = ConfMock; 