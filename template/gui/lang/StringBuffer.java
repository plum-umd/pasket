package java.lang;

public class StringBuffer {
  char[] value;
  int count;

  public StringBuffer(String str) {
    value = str;
  }

  public void setCharAt(int i, char c) {
    value[i] = c;
  }

  public String toString() {
    return value;
  }

}
