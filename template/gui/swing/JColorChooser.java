package javax.swing;

public class JColorChooser extends JComponent {
  public JColorChooser();

  public ColorSelectionModel getSelectionModel();
  public void setSelectionModel(ColorSelectionModel newModel);

  public Color getColor();
  public void setColor(Color color);
}
