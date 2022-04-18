import pytest

from ContentEngineerStudio.utils.hash_messages import Hash


@pytest.fixture
def setUp():
    hash = Hash()
    return hash

@pytest.fixture
def make_list():
    list = [
        "Section 1.10.32 of "'de Finibus Bonorum et Malorum'", written by Cicero in 45 BC",
        "Sed ut perspiciatis unde omnis iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo. Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.",
        "But I must explain to you how all this mistaken idea of denouncing pleasure and praising pain was born and I will give you a complete account of the system, and expound the actual teachings of the great explorer of the truth, the master-builder of human happiness. No one rejects, dislikes, or avoids pleasure itself, because it is pleasure,",
        "but because those who do not know how to pursue pleasure rationally encounter consequences that are extremely painful. Nor again is there anyone who loves or pursues or desires to obtain pain of itself, because it is pain, but because occasionally circumstances occur in which toil and pain can procure him some great pleasure. To take a trivial example, which of us ever undertakes laborious physical exercise, except to obtain some advantage from it? But who has any right to find fault with a man who chooses to enjoy",
        "a pleasure that has no annoying consequences, or one who avoids a pain that produces no resultant pleasure?"
        ]
    return list

def test_can_pass_list_to_hash_function(setUp, make_list):
    setUp.hash_list(make_list)

def test_can_handle_empty_list_as_input(setUp):
    assert setUp.hash_list([]) == False

def test_can_handle_invalid_input(setUp):
    assert setUp.hash_list("bla") == False

def test_returns_list_with_list_as_input(setUp, make_list):
    result = setUp.hash_list(make_list)
    assert  isinstance(result, list) == True

def test_input_and_output_have_same_length(setUp, make_list):
    result = setUp.hash_list(make_list)
    assert  len(result) == len(make_list)

def test_can_hash_messages_without_collisions(setUp, make_list):
    result = setUp.hash_list(make_list)
    assert len(make_list) == len(set(result))

def test_hashing_returns_integers(setUp, make_list):
    result = setUp.hash_list(make_list)
    result = [True for x in result if isinstance(x, int)]
    assert len(set(result)) == 1
    assert result[0] == True
