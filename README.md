# streck

Streck is a system implementing a basic credit-based sales terminal. It is written in Python using the [Flask][flask] framework, but is not intended to be served publically. Instead, it is supposed to run locally and served to a local browser only.

There is no focus on security (the administration interface is not password protected, and no measures to stop XSS issues and similar are taken) since the intended environment shouldn't require this.

There is basic category support (without administration interface), and it is possible to edit, add and disable users from the administration interface. Products are also managed through a simple interface.

[flask]: http://flask.pocoo.org

## Using streck

Using streck could be difficult, but shouldn't be. Make sure you have the dependencies (Python, Flask and SQLite3) and the rest should be easy. Flask and SQLite3 are easily installed with `pip`:

	pip install Flask sqlite3

### Getting started

Start by cloning this repository:

	git clone https://github.com/urdh/streck.git

Now, make sure to create the database you'll be running with (by default, this resides in the current working directory):

	sqlite3 streck.db < streck/schema.sql

Great! Now, run `streck.py` and use your browser to add products and users:

	./streck.py

### Configuration

Configuration is done by editing `streck/__init__.py` to set the proper application variables (this may change in the future, subject to popular demand). The following options are available:

	app.config['DATABASE'] = './streck.db'      # Location of database
	app.config['PAID_BARCODE'] = 'BETALT'       # Barcode used to reset (or "pay") a user debt
	app.config['UNDO_BARCODE'] = 'undo'         # Barcode used to undo a purchase
	app.config['LOGOUT_BARCODE'] = 'log out'    # Barcode used to log users out (this happens automatically after 15 seconds or when another user logs in anyway)
	app.config['UPLOAD_FOLDER'] = './pictures/' # Location of uploaded images

You could also change the secret key; this affects cookies and should not be relevant if you're running streck in a local environment. Session cookies are only used to flash messages at the user.

### Using the program

Streck is fairly simple to use, basically only requiring a cheap computer and a USB barcode reader (as well as mouse/keyboard for administration).

To buy things, a user first scans the barcode that identifies him and logs him in. Then, the user scans the barcode of whatever he wants to buy. It's as simple as that. Products may also be scanned without being logged in, displaying their price.

### The conversion tool

The conversion tool included in the repository, `./convert.py`, converts data from an earlier, Java-based software solving a similar problem. That software is not publically available, and thus the conversion tool will probably not be very useful to you. Just ignore it.

## Contributing

All development of Streck is done on Github. If you'd like to contribute, please raise issues and submit pull requests using the Github interface.

Pull requests are best made from separate branches (i.e. one branch per request/feature), not from `master`. Pull requests also imply that you agree to licensing your code under the relevant license.

## Planned improvements

* Internationalization/translation support. This is on hold, see the `babel` branch.
* Statistics including most popular product, most avid user and timeseries graphs generated with [dygraphs][dygraphs]. See the `stats` branch.

[dygraphs]: https://github.com/danvk/dygraphs

## License

	Copyright (c) 2012 Simon Sigurdhsson <sigurdhsson@gmail.com>
	
	Permission to use, copy, modify, and distribute this software for any
	purpose with or without fee is hereby granted, provided that the above
	copyright notice and this permission notice appear in all copies.
	
	THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
	WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
	MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
	ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
	WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
	ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
	OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
