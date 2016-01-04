package rasket;

import java.util.List;
import java.util.LinkedList;

// More complicated template. Perhaps the final version of what we want the
// code to become for design pattern transformation.

class AbstractButton {
}

public class JButton extends AbstractButton {
    private List<ActionListener> olist = new LinkedList<ActionListener>();

    public JButton() {
	return;
    }

    public void addActionListener(ActionListener obs) {
        olist.add(obs);
    }

    public void removeActionListener(ActionListener obs) {
        olist.remove(obs);
    }
    
    public void fireActionPerformed(ActionEvent e) {
        for (int i = 0; i < olist.size(); i++) {
            ActionListener o = olist.get(i);
            o.actionPerformed(e);
        }
    }
}
