-- mariadb script to create the complete schema for the application

DROP TABLE IF EXISTS artists;
DROP TABLE IF EXISTS albums;
DROP TABLE IF EXISTS scan_results;

CREATE TABLE IF NOT EXISTS artists (
  id INTEGER NOT NULL,
  name TEXT NOT NULL,
  link TEXT,
  picture TEXT,
  picture_small TEXT,
  picture_medium TEXT,
  picture_big TEXT,
  picture_xl TEXT,
  nb_album INTEGER,
  nb_fan INTEGER,
  radio BOOLEAN,
  tracklist TEXT,
  type TEXT,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS albums (
  id INTEGER NOT NULL,
  title TEXT NOT NULL,
  link TEXT,
  cover TEXT,
  cover_small TEXT,
  cover_medium TEXT,
  cover_big TEXT,
  cover_xl TEXT,
  genre_id INTEGER,
  fans INTEGER,
  release_date DATE,
  record_type TEXT,
  explicit_lyrics BOOLEAN,
  artist_id INTEGER NOT NULL,
  PRIMARY KEY (id)
);

CREATE TABLE IF NOT EXISTS scan_results (
  id INTEGER PRIMARY KEY,
  folder_path TEXT NOT NULL,
  scan_dump TEXT NOT NULL,
  scan_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);