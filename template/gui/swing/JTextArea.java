package javax.swing;

public class JTextArea extends JTextComponent {
  public JTextArea();
  public JTextArea(Document doc);
  public JTextArea(Document doc, String text, int rows, int columns);
  public JTextArea(int rows, int columns);

  // TODO: builder pattern?
  public void append(String str) {
    // setText(getText() + str); // TODO: String concatenation
    setText(str);
  }
}
