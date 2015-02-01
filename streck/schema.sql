drop table if exists users;
drop table if exists products;
drop table if exists categories;
drop table if exists transactions;
create table users (
	id integer primary key autoincrement,
	barcode text unique not null,
	enabled boolean not null,
	name text not null,
	image text,
	notes text
);
create table products (
	id integer primary key autoincrement,
	barcode text unique not null,
	name text not null,
	price real not null,
	category integer not null,
	image text,
	notes text,
	foreign key(category) references categories(id)
);
create table categories (
	id integer primary key autoincrement,
	name text not null
);
create table transactions (
	id integer primary key autoincrement,
	added text not null,
	user integer not null,
	product integer,
	price real not null,
	notes text,
	foreign key(user) references user(id),
	foreign key(product) references product(id)
);
insert into categories values (null, "Öl");
insert into categories values (null, "Ickeöl");
insert into users values (null, "Jobbmat", 1, "Jobbmat", null, "Jobbmatskonto");
