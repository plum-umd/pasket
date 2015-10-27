import java.lang.reflect.Method;
import java.io.File;
import java.io.FileFilter;
import java.net.URL;

public class Main {

  static String[] getSubs(String path) {
    File dir = new File(path);
    File[] subs = dir.listFiles(new FileFilter() {
        public boolean accept(File sub) {
          return sub.isDirectory();
        }
    });
    String [] r = new String [subs.length];
    for (int i = 0; i < subs.length; i++) {
      r[i] = subs[i].getName();
    }
    return r;
  }

  static String[] concat(String[] a, String[] b) {
    String[] c = new String[a.length + b.length];
    System.arraycopy(a, 0, c, 0, a.length);
    System.arraycopy(b, 0, c, a.length, b.length);
    return c;
  }

  static <T> boolean includes(T[] arr, T elt) {
    for (T a : arr) {
      if (a.equals(elt)) return true;
    }
    return false;
  }

  public static void main(String[] args) throws Exception {
    URL m_java = Main.class.getProtectionDomain().getCodeSource().getLocation();
    String src = new File(m_java.toURI()).getParent() + "/src";
    String[] patterns = getSubs(src + "/pattern");
    String[] tutorials = getSubs(src + "/tutorial");
    String[] all = concat(patterns, tutorials);

    String[] targets = args.length == 0 ? all : args;
    if (args.length == 1) {
      if (args[0].equals("patterns")) { targets = patterns; }
      else if (args[0].equals("tutorials")) { targets = tutorials; }
    }

    for (String t : targets) {
      String name = "";
      if (includes(patterns, t)) {
        name = "pattern." + t + ".Test";
      } else if (includes(tutorials, t)) {
        name = "tutorial." + t + ".Test";
      } else { continue; }
      try {
        Class clazz = Class.forName(name);
        Method mtd = clazz.getDeclaredMethod("main", args.getClass());
        mtd.invoke(null, new Object[] { args });
      } catch (Exception e) {
        e.printStackTrace(System.out);
      }
    }
  }

}
