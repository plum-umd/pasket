package javax.swing;

public class JFrame extends Frame {
  public static final int EXIT_ON_CLOSE = 3;

  public JFrame();
  public JFrame(String name);

  public Container getContentPane();
  public void setContentPane(Container p);

  public int getDefaultCloseOperation();
  public void setDefaultCloseOperation(int operation);

  public JMenuBar getJMenuBar();
  public void setJMenuBar(JMenuBar menubar);
}
