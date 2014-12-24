package javax.swing;

public class JFileChooser extends JComponent {
  public static final int APPROVE_OPTION = 0;
  public static final int CANCEL_OPTION = 1;

  public static final int OPEN_DIALOG = 0;
  public static final int SAVE_DIALOG = 1;
  public static final int CUSTOM_DIALOG = 2;

  public File getSelectedFile();

  public void setDialogType(int dialogType);

  // TODO: return value depends on user input
  public int showDialog(Component parent, String approveButtonText) {
    return CANCEL_OPTION;
  }

  public int showOpenDialog(Component parent) {
    // TODO: how to figure out Open-specific setting?
    setDialogType(OPEN_DIALOG);
    // TODO: how to determine this internal usage?
    return showDialog(parent, "");
  }

  public int showSaveDialog(Component parent) {
    // TODO: how to figure out Save-specific setting?
    setDialogType(SAVE_DIALOG);
    // TODO: how to determine this internal usage?
    return showDialog(parent, "");
  }
}
