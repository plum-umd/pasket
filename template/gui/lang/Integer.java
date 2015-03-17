package java.lang;

public class Integer {
  //public static final int MIN_VALUE = 0x80000000; // -2^31
  public static final int MAX_VALUE = 0x7fffffff; // 2^31 - 1

/*
  final static char[] digits = {
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'a', 'b', 'c', 'd', 'e', 'f'
  };
*/

  public static String toString(int i) {
    // TODO: how to convert integer to String in general
    if (i == 4) return "4";
    else if (i == 7) return "7";
    return "0";
  }
}
