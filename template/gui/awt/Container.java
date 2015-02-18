package java.awt;

public class Container extends Component {
  public Component add(Component comp) {
    // TODO: how to synthesize other behavior in detail?
    return comp; // TODO: how can we synthesize this return statement as well?
  }
  // TODO: method overloading
  //public void add(Component comp, Object constraints); // TODO: casting
  //public void add(Component comp, String constraints);

  public LayoutManager getLayout();
  public void setLayout(LayoutManager mgr);
}
