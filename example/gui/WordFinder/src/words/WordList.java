package words;

import java.io.FileInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.io.StreamTokenizer;
import java.text.Collator;
import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Set;
import java.util.TreeSet;

/**
 * A WordList is a set of words that is searchable by substring.  
 * A word is defined as a sequence of letters
 * (upper case or lower case) or apostrophes (to allow contractions
 * like "don't").  WordLists ignore alphabetic case when
 * searching and sorting. 
 */
public class WordList {
    private final List<String> words = new ArrayList<String>();
    
    /*
     * Rep invariant:
     *      words != null
     */
    
    /**
     * Make an empty WordList.
     */
    public WordList() { }
    
    /**
     * Load a stream into this word set.
     * @requires in is an open stream consisting of a sequence of words.
     * @effects Removes all the words from this word set and replaces 
     * them with the words found in the stream (treating punctuation,
     * whitespace, and numbers as delimiters between words).
     * @throws IOException if an error occurred while reading the stream
     */
    public void load(InputStream in) throws IOException {
        Collator c = Collator.getInstance();
        c.setStrength(Collator.PRIMARY);
        Set<String> s = new TreeSet<String>(c);
        
        StreamTokenizer tok = new StreamTokenizer(new InputStreamReader(in));
        tok.resetSyntax();
        tok.wordChars('a', 'z');
        tok.wordChars('A', 'Z');
        tok.wordChars('\'', '\'');
        
        while (tok.nextToken() != StreamTokenizer.TT_EOF) {
            if (tok.ttype == StreamTokenizer.TT_WORD)
                s.add(tok.sval);
        }
        
        words.clear();
        words.addAll(s);
    }
    
    /**
     * Find words containing a given substring.
     * @param s Substring to search for
     * @requires s != null
     * @return list of words in this word set (sorted case-insensitively)
     * that contain the substring s (matched case-insensitively).  A
     * word appears at most once in the returned list.
     */
    public List<String> find(String s) {
        if (s.length() == 0) {
            return Collections.unmodifiableList(words);
        }
        
        s = s.toLowerCase();
        List<String> l = new ArrayList<String>();
        for (String word : words) {
            if (word.toLowerCase().indexOf(s) != -1)
                l.add(word);
        }
        return l;
    }
    
    /**
     * Main method.  Demonstrates how to use this class.
     * @param args Command-line arguments.  Ignored.
     */
    public static void main(String[] args) throws IOException {
        WordList words = new WordList ();
        
        InputStream in = new FileInputStream("words");
        
        words.load(in);
        
        // Print all the words containing "ph"
        List<String> matches = words.find("ph");
        for (String match : matches) {
            System.out.println(match);
        }
    }    
}
