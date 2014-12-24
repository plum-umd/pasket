package java.lang;

public class StringBuffer {
  char[] value;
  int count;

  StringBuffer(String str) {
    value = str;
  }

  void setCharAt(int i, char c) {
    value[i] = c;
  }

  String toString() {
    return value;
  }

}
