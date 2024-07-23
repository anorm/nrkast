-- create-http-cache
-- depends:
CREATE TABLE http_cache (
  key varchar(100) PRIMARY KEY,
  value bytea
);
