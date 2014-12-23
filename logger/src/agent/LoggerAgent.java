// http://extranet.ipl.be/OOMADB/document/IPL_cours/COO/logging-at-loadingTime.htm

package agent;

import java.lang.instrument.ClassFileTransformer;
import java.lang.instrument.Instrumentation;
import java.util.Arrays;
import java.util.Date;
import java.util.Set;
import java.util.HashSet;
import java.security.ProtectionDomain;
import javassist.ClassPool;
import javassist.CtClass;
import javassist.CtField;
import javassist.CtBehavior;
import javassist.NotFoundException;
import javassist.CannotCompileException;
import javassist.expr.ExprEditor;
import javassist.expr.MethodCall;

public class LoggerAgent implements ClassFileTransformer {

  // add agent
  public static void premain
      (String agentArgument, Instrumentation instrumentation) {
    if (agentArgument != null) {
      String[] args = agentArgument.split(",");
      Set argSet = new HashSet(Arrays.asList(args));

      if (argSet.contains("time")) {
        System.err.println("Start at " + new Date());
        Runtime.getRuntime().addShutdownHook(new Thread() {
          public void run() {
            System.err.println("Stop at " + new Date());
          }
        });
      }
      // ... more agent option handling here
    }
    instrumentation.addTransformer(new LoggerAgent());
  }

  String def = "private static java.util.logging.Logger _log;";
  String ifLog = "if (_log.isLoggable(java.util.logging.Level.INFO))";

  static private boolean includes(String[] ignores, String target) {
    for (String ignore : ignores) {
      if (target.startsWith(ignore) || target.endsWith(ignore))
        return true;
    }
    return false;
  }

  String[] libraries = {
    "apple/", "com/apple/", "sun/", "com/sun/",
    "java/", "javax/",
  };

  // when logging API usage, ignore some classes that generate too much info
  String[] c_ignores = {
    "java/util", // "java/util/logging/Logger",
    "java/lang", // "java/lang/StringBuilder", "java/lang/StringBuffer"
    "java/io", // "java/io/PrintStream"
  };

  // The transform(...) method calls doClass(...) if the class name does not
  // start with any of the prefixes it has been told to ignore (note that the
  // separators are slashes, not dots).

  // instrument class
  public byte[] transform(ClassLoader loader, String className,
      Class clazz, ProtectionDomain domain, byte[] bytes) {

    // do not instrument libraries
    if (LoggerAgent.includes(libraries, className)) return bytes;

    return doClass(className.replace('/','.'), clazz, bytes);
  }

  // java.lang.reflect.InvocationHandler.invoke()
  String[] m_ignores = { "invoke" };

  // The doClass(...) method uses javassist to analyze the byte stream. If it
  // is a real class, a logger field is added and initialized to the name of
  // the class. Each non-empty method is then processed with doMethod(...).
  // The finally-clause ensures that the class definition is removed again
  // from the javassist pools to keep memory usage down.
  //
  // Note: The logger variable has been named _log. In a production version an
  // unused variable name should be found and used.

  private byte[] doClass(String name, Class clazz, byte[] b) {
    ClassPool pool = ClassPool.getDefault();
    CtClass cl = null;
    try {
      cl = pool.makeClass(new java.io.ByteArrayInputStream(b));
      if (!cl.isInterface()) {

        CtField field = CtField.make(def, cl);
        String getLogger = "java.util.logging.Logger.getLogger("
            + name + ".class.getName());";
        cl.addField(field, getLogger);

        CtBehavior[] methods = cl.getDeclaredBehaviors();
        for (int i = 0; i < methods.length; i++) {
          if (methods[i].isEmpty() ||
              LoggerAgent.includes(m_ignores, methods[i].getName())) continue;

          doMethod(name, methods[i]);
        }
        b = cl.toBytecode();
      }
    } catch (Exception e) {
      System.err.println("Could not instrument " + name
          + ",  exception : " + e.getMessage());
    } finally {
      if (cl != null) {
        cl.detach();
      }
    }
    return b;
  }

  // The doMethod(...) class creates "_log.info(...)" snippets to insert at
  // the beginning and end of each method. Both contain the parameters (as
  // they may have changed), and the end method statement contain the return
  // value for non-void methods (which is available as $_ in the javassist
  // compiler).

  private void doMethod(String name, CtBehavior method)
      throws NotFoundException, CannotCompileException {

    // System.out.println("instrument: " + name + "." + method.getName());

    String methodName = name + "." + method.getName();
    String signature = JavassistHelper.getSignature(method);
    String returnVal = JavassistHelper.returnValue(method);

    // logging method entrance
    method.insertBefore(ifLog + "_log.info(\"> "
        + methodName + "(\" " + signature + "+ \")\"" + ");");

    // logging method exit
    method.insertAfter(ifLog + "_log.info(\"< "
        + methodName + "(\" " + returnVal + "+ \")\"" + ");");

    // logging API usage
    method.instrument(new ExprEditor() {
      public void edit(MethodCall mc) throws CannotCompileException {
        try {
          CtBehavior callee = mc.getMethod();
          String cname = mc.getClassName();
          // System.out.println("api: " + cname + "." + mc.getMethodName());
          String cname_slash = cname.replace('.', '/');
          // check whether it's library call
          if (! LoggerAgent.includes(libraries, cname_slash)) return;
          // among library calls, ignore some classes
          if (  LoggerAgent.includes(c_ignores, cname_slash)) return;

          String api = cname + "." + mc.getMethodName();
          String sig = JavassistHelper.getSignature(callee);
          String ret = JavassistHelper.returnValue(callee);

          // before API use
          String api_ent = ifLog + "_log.info(\"> "
              + api + "(\" " + sig + "+ \")\"" + ");";

          // after API use
          String api_ext = ifLog + "_log.info(\"< "
              + api + "(\" " + ret + "+ \")\"" + ");";

          mc.replace("{" + api_ent + "$_ = $proceed($$);" + api_ext + "}");
        }
        catch (NotFoundException ne) {
          System.err.println("Could not log " + mc.getMethodName()
            + ",  exception : " + ne.getMessage());
        }
      }
    });
  }
}
