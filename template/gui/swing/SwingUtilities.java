package javax.swing;

public class SwingUtilities implements SwingConstants {

  public static void invokeLater(Runnable doRun) {
    EventQueue.invokeLater(doRun);
  }
/*
  public static void invokeAndWait(Runnable doRun) {
    EventQueue.invokeAndWait(doRun);
  }
*/
}
