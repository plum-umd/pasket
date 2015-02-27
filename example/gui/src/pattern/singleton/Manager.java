package pattern.singleton;

import java.util.Map;
import java.util.HashMap;

class Manager {

  private Map<Integer, Object> _objs;

  static final Integer water = new Integer(0);
  static final Integer power = new Integer(1);

  private Manager () {
    _objs = new HashMap<Integer, Object>();
  }

  private static Manager _instance = null;

  static Manager getManager() {
    if (_instance == null) {
      _instance = new Manager();
    }
    return _instance;
  }

  Object getResource(Integer key) {
    Object res = _objs.get(key);
    if (res == null) {
      res = new Resource(key);
      _objs.put(key, res);
    }
    return res;
  }

}
