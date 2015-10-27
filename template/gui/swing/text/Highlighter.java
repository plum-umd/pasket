package javax.swing.text;

public interface Highlighter {

  public void addHighlight(int p0, int p1, HighlightPainter p);

  public void removeAllHighlights();

  public static interface HighlightPainter {
    public void paint(Graphics g, int p0, int p1, Shape bounds, JTextComponent c);
  }

}
