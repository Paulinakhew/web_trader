'use strict';
module.exports = str => {
	const pth = str || process.cwd();

	if (pth === '/') {
		return ['/'];
	}

	const parts = pth.split(/[/\\]/);

	return parts.map((el, i) => parts.slice(0, parts.length - i).join('/').replace(/^$/, '/'));
};
