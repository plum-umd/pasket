package java.lang;

public class String implements CharSequence {
    char[] _value;
    int _count;

    // use this constructor as it includes "count"
    // ignore offset at the moment
    public String(char[] ca, int offset, int count) {
        _value = ca;
        _count = count;
    }

    public int length() {
        return _count;
    }

    public String toString() {
        return this;
    }

    public boolean equals(String s) {
        return _value == s._value;
    }

    public int indexOf(String str) {
        return indexOf(ch, 0);
    }

    public int indexOf(String str, int fromIndex) {
        int src_len = _count;
        int tgt_len = str._count;

        if (fromIndex >= src_len) {
            if (tgt_len == 0) return src_len;
            else return -1;
        }
        if (fromIndex < 0) fromIndex = 0;
        if (tgt_len == 0) return fromIndex;

        int index = fromIndex;
        int gap = src_len - tgt_len;
        while (index <= gap) {
            boolean mismatch = false;
            int i = 0;
            while (i < tgt_len && !mismatch) {
                if (_value[index + i] != str._value[i]) {
                    mismatch = true;
                }
                i = i + 1;
            }
            if (!mismatch) return index;
            index = index + 1;
        }
        return -1;
    }

}
