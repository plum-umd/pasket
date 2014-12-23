// http://extranet.ipl.be/OOMADB/document/IPL_cours/COO/logging-at-loadingTime.htm

package agent;

import javassist.CtBehavior;
import javassist.CtClass;
import javassist.CtConstructor;
import javassist.CtMethod;
import javassist.Modifier;
import javassist.NotFoundException;
import javassist.bytecode.AccessFlag;
import javassist.bytecode.CodeAttribute;
import javassist.bytecode.LocalVariableAttribute;

import java.util.Arrays;
import java.util.Set;
import java.util.HashSet;

public class JavassistHelper {

  static final Set<Class> WRAPPER_TYPES = new HashSet(Arrays.asList(
    Boolean.class, Character.class, Byte.class, Short.class, Integer.class,
    Long.class, Float.class, Double.class, Void.class));

  static boolean isWrapperType(Class clazz) {
    return WRAPPER_TYPES.contains(clazz);
  }

  public static String printObj(Object arg) {
    String ret = "";
    if (arg == null) {
      ret = "null";
    } else if (isWrapperType(arg.getClass())) {
      ret = arg.toString();
    } else if (arg.getClass() == String.class) {
      ret = "\"" + ((String)arg).replace("\n","\\n") + "\"";
    } else if (arg.getClass() == Class.class) {
      ret = ((Class)arg).getName();
    } else {
      ret = arg.getClass().getName() + "@" + System.identityHashCode(arg);
    }
    return ret;
  }

  static String printArg(CtClass ty, String arg)
      throws NotFoundException {
    String ret = "";
    CtClass arrayOf = ty.getComponentType();
    // use Arrays.asList() to render array of objects
    if (arrayOf != null && !arrayOf.isPrimitive()) {
      ret = "java.util.Arrays.asList(" + arg + ")";
    } else if (ty.isPrimitive()) {
      ret = arg;
    } else {
      // to avoid NullPointerException, distinguish arg at runtime
      ret = "agent.JavassistHelper.printObj(" + arg + ")";
    }
    return ret;
  }

  static String returnValue(CtBehavior method)
      throws NotFoundException {
    String returnValue = "";
    if (methodReturnsValue(method)) {
      CtClass returnType = ((CtMethod)method).getReturnType();
      returnValue = " + " + printArg(returnType, "$_");
    }
    else if (methodReturnsObj(method)) {
      CtClass owner = method.getDeclaringClass();
      returnValue = " + " + printArg(owner, "$0");
    }
    return returnValue;
  }

  // jsjeon: to track objects, print the hash value after <init>
  private static boolean methodReturnsObj(CtBehavior method)
      throws NotFoundException {
    if (method instanceof CtConstructor)
      // skip <clinit>
      return !((CtConstructor)method).isClassInitializer();
    else
      return false;
  }

  // jsjeon: this was buggy, for Constructor can't be cast to CtMethod
  private static boolean methodReturnsValue(CtBehavior method)
      throws NotFoundException {
    boolean isConstructor = method instanceof CtConstructor;

    boolean isMethod = method instanceof CtMethod;
    boolean isVoidMethod = isMethod;
    if (isMethod) {
      CtClass returnType = ((CtMethod)method).getReturnType();
      String returnTypeName = returnType.getName();
    
      isVoidMethod = "void".equals(returnTypeName);
    }

    boolean methodReturnsValue = (isVoidMethod || isConstructor) == false;
    return methodReturnsValue;
  }

  static String getSignature(CtBehavior method)
      throws NotFoundException {
    CtClass parameterTypes[] = method.getParameterTypes();

    CodeAttribute codeAttribute = method.getMethodInfo().getCodeAttribute();

    // LocalVariableAttribute locals =
    //   (LocalVariableAttribute) codeAttribute.getAttribute("LocalVariableTable");

    StringBuffer sb = new StringBuffer();
    // jsjeon: want to print "this" as well
    boolean notStatic = method instanceof CtMethod
        && 0 == (method.getModifiers() & AccessFlag.STATIC);
    if (notStatic) {
      CtClass owner = method.getDeclaringClass();
      sb.append(" + " + printArg(owner, "$0"));
    }
    for (int i = 0; i < parameterTypes.length; i++) {
      if (notStatic || i > 0) {
        sb.append(" + \", \" ");
      }

      CtClass parameterType = parameterTypes[i];

      sb.append(" + \"");
      // jsjeon: 1=value1, 2=value2, ... => value1, value2, ...
      // sb.append(parameterNameFor(method, locals, i));
      // sb.append("\" + \"=");

      sb.append("\" + " + printArg(parameterType, "$"+(i+1)));
    }

    String signature = sb.toString();
    return signature;
  }

  // static String parameterNameFor(CtBehavior method,
  //     LocalVariableAttribute locals, int i) {
  //   if (locals == null) {
  //     return Integer.toString(i + 1);
  //   }

  //   if (Modifier.isStatic(method.getModifiers())) {
  //     return locals.variableName(i);
  //   }

  //   // skip #0 which is reference to "this"
  //   return locals.variableName(i + 1);
  // }

}
