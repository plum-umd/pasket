package javax.swing.text;

public class DefaultHighlighter implements Highlighter {

  public DefaultHighlighter();

  public void addHighlight(int p0, int p1, HighlightPainter p);

  public void removeAllHighlights();

  public class DefaultHighlightPainter implements Highlighter.HighlightPainter {
    public DefaultHighlightPainter(Color c);

    public void paint(Graphics g, int p0, int p1, Shape bounds, JTextComponent c);
  }

}
