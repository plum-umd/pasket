package java.lang;

public class String {
    char[] value;
    int count;

    public String(char[] ca) {
        count = 0;
        while (ca[count] != 0) {
            value[count] = ca[count];
            count = count + 1;
        }
    }

    public String toString() {
        return value;
    }

    public boolean equals(String s) {
        return value == s.value;
    }

    public int length() {
        return count;
    }

    public int indexOf(String str) {
        return indexOf(ch, 0);
    }

    public int indexOf(String str, int fromIndex) {
        int src_len = count;
        int tgt_len = str.count;

        if (fromIndex >= src_len) {
            if (tgt_len == 0) return src_len;
            else return -1;
        }
        if (tgt_len == 0) return fromIndex;

        int index = fromIndex;
        int gap = src_len - tgt_len;
        while (index <= gap) {
            boolean mismatch = false;
            int i = 0;
            while (i < tgt_len) {
                if (value[index + i] != str.value[i]) {
                    mismatch = true; break;
                }
                i = i + 1;
            }
            if (!mismatch) return index;
            index = index + 1;
        }
        return -1;
    }

}
