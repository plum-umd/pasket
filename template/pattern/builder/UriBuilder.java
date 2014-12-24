class UriBuilder {

  @Set(scheme)
  private String scheme;

  @Set(authority)
  private String authority;

  @Set(path) @Append
  private String path;

  @Append
  private String query;

  @Assemble
  String build();

}
