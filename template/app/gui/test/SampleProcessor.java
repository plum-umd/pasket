import java.util.*;
import java.lang.reflect.*;



class SampleProcessor {
    public static Queue<String> process(Queue<String> mc) {
        Queue<String> processed = new ArrayDeque<String>();
        for (String c : mc) {
            processed.add(manualReplace(automaticReplace(c)));
        }
        return processed;
    }
    
    private static boolean hasMethod(Class c, String mname) {
        Method[] mtds = c.getDeclaredMethods();
        for (int i = 0; i < mtds.length; i++) {
            if (mtds[i].getName().equals(mname))
                return true;
        }
        return false;
    }
    
    private static String automaticReplace(String l) {
        
        int argIdx = l.indexOf("(");
        
        String callName = l.contains("> ") ?
        l.substring(l.indexOf("> ") + 2, argIdx) :
        l.substring(l.indexOf("< ") + 2, argIdx) ;
        
        int mtdIdx = callName.lastIndexOf(".");
        
        String className = callName.substring(0, mtdIdx);
        String methodName = callName.substring(mtdIdx + 1, callName.length());
        
        if (className.contains(methodName))
            // means the method is a constructor
        {
            return l;
        }
        
        try {
            Class c = Class.forName(className);
            
            while (! hasMethod(c, methodName)) {
                c = (Class)c.getGenericSuperclass();
            }
            
            //System.out.println("replace " + callName + " with " + c.getName() + "." + methodName);
            return l.replace(callName, c.getName() + "." + methodName);
        } catch (ClassNotFoundException cnfe) {
            return l;
        }
    }
    
    private static String manualReplace(String l) {
        l = l.replaceFirst("JButton.setVerticalTextPosition", "AbstractButton.setVerticalTextPosition");
        l = l.replaceFirst("JButton.setHorizontalTextPosition", "AbstractButton.setHorizontalTextPosition");
        l = l.replaceFirst("JButton.setMnemonic", "AbstractButton.setMnemonic");
        l = l.replaceFirst("JButton.setActionCommand", "AbstractButton.setActionCommand");
        l = l.replaceFirst("JButton.setEnabled", "AbstractButton.setEnabled");
        l = l.replaceFirst("JButton.addActionListener", "AbstractButton.addActionListener");
        l = l.replaceFirst("JButton.setTool", "JComponent.setTool");
        l = l.replaceFirst("javax.swing.JFrame.setVisible", "java.awt.Component.setVisible");
        l = l.replaceFirst("java.awt.Window.setVisible", "java.awt.Component.setVisible");
        l = l.replaceFirst("javax.swing.JPanel.add", "java.awt.Container.add");
        l = l.replaceFirst("javax.swing.JToolBar.add\\(", "java.awt.Container.add\\(");
        l = l.replaceFirst("javax.swing.AbstractButton.setEnabled", "java.awt.Component.setEnabled");
        
        l = l.replaceAll("tutorial.", "swings.");
        l = l.replaceAll("javax.swing.colorchooser.ColorSelectionModel", "javax.swing.colorchooser.DefaultColorSelectionModel");
        l = l.replaceAll("javax.swing.text.Document.getLength", "javax.swing.text.AbstractDocument.getLength");
        
        return l;
    }
}

