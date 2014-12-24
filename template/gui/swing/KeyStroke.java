package javax.swing;

public class KeyStroke extends AWTKeyStroke {
  // TODO: must be @Multiton,
  // as it should return the same instance for the same keyCode
  @Factory
  public static KeyStroke getKeyStroke(int keyCode, int modifiers);
}
