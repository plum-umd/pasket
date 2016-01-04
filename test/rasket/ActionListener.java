package rasket;

import java.util.List;
import java.util.LinkedList;

// More complicated template. Perhaps the final version of what we want the
// code to become for design pattern transformation.


public interface ActionListener {
    void actionPerformed(ActionEvent e);
}

class EventObject {
    Object getSource() {return null;}
}

