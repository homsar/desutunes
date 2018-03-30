# Test the split_id3_title function from processfile.py

from desutunes.processfile import split_id3_title


def test_split_id3_title_simple():
    assert (split_id3_title("Lion (Macross Frontier OP2)") == (
        "Lion", "Macross Frontier OP2"))


def test_split_id3_title_extra_bracket():
    assert (split_id3_title(
        "CHANGE!!!! (M@STER VERSION) "
        "(The iDOLM@STER OP2)") == ("CHANGE!!!! (M@STER VERSION)",
                                    "The iDOLM@STER OP2"))


def test_split_id3_title_double_bracket():
    assert (split_id3_title(
        "CHANGE!!!! ((M@STER VERSION)) "
        "(The iDOLM@STER OP2)") == ("CHANGE!!!! ((M@STER VERSION))",
                                    "The iDOLM@STER OP2"))


def test_missing_detail():
    assert (split_id3_title("Ai oboeteimasu ka") == ("Ai oboeteimasu ka",
                                                     None))
