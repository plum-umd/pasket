package pattern.builder;

class UriBuilder {

  private String scheme;
  private String authority;
  private String path;
  private String query;

  public UriBuilder() { }

  UriBuilder scheme(String scheme) {
    this.scheme = scheme;
    return this;
  }

  UriBuilder authority(String authority) {
    this.authority = authority;
    return this;
  }

  UriBuilder path(String path) {
    this.path = path;
    return this;
  }

  UriBuilder appendPath(String path) {
    if (this.path == null) {
      this.path = path;
    } else {
      this.path += "/" + path;
    }
    return this;
  }

  UriBuilder appendQueryParameter(String key, String value) {
    String param = key + "=" + value;
    if (this.query == null) {
      this.query = param;
    } else {
      this.query += "&" + param;
    }
    return this;
  }

  String build() {
    return scheme + "://" + authority + "/" + path + "?" + query;
  }

/* this method prevents the logger from being carried out!
  public String toString() {
    return this.build();
  }
*/
}
