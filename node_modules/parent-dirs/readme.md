# parent-dirs [![Build Status](https://travis-ci.org/sindresorhus/parent-dirs.svg?branch=master)](https://travis-ci.org/sindresorhus/parent-dirs)

> Get an array of parent directories including itself


## Install

```
$ npm install --save parent-dirs
```


## Usage

```js
const parentDirs = require('parent-dirs');

parentDirs(__dirname);
/*
[
	'/Users/sindresorhus/dev/parent-dirs',
	'/Users/sindresorhus/dev',
	'/Users/sindresorhus',
	'/Users',
	'/'
]
*/
```


## API

### parentDirs(cwd)

#### cwd

Type: `string`<br>
Default: `process.cwd()`

Directory starting point to return paths from.


## License

MIT © [Sindre Sorhus](https://sindresorhus.com)
