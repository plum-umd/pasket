package pattern.proxy;

import java.lang.reflect.InvocationHandler;
import java.lang.reflect.Method;

class AccessController implements InvocationHandler {

  private IStudent _student;
  private String _profile = null;

  public AccessController(IStudent student) {
    this._student = student;
  }

  public Object invoke(Object proxy, Method m, Object[] args) throws Exception {
    if (m.getName().startsWith("setGrade")) {
      System.out.println("Stduents cannot set their own grade");
    }
    else if (m.getName().startsWith("getProfile")) {
      if (this._profile == null) {
        this._profile = (String)m.invoke(this._student, args);
      }
      return this._profile;
    }
    else if (m.getName().startsWith("get")) {
      return m.invoke(this._student, args);
    }
    return null;
  }

}
