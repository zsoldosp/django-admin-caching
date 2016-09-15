from django_admin_caching.patching import Patched
import pytest
from testapp.six import Mock
from testapp import to_be_patched


class Greeter(object):
    def hello(self, name):
        return 'Hello {}!'.format(name)


def test_patching_has_orig_item_and_wrapper():
    mock = Mock()
    p = Patched(orig=Greeter.hello, new=mock)
    assert p.orig == Greeter.hello
    assert p.new == mock


@pytest.mark.parametrize(
    'args,kwargs', [
        [('World',), {}],
        [tuple(), {'name': 'Universe'}],
    ], ids=['args', 'kwargs']
)
def test_patched_is_called_with_caller_args_and_orig_method(args, kwargs):
    mock = Mock()
    p = Patched(orig=Greeter.hello, new=mock)
    g = Greeter()

    # call via args
    p(g, *args, **kwargs)
    assert mock.called
    should_have_been_called_with_args = (Greeter.hello, g, ) + args
    should_have_been_called_with_kwargs = kwargs
    mock.assert_called_once_with(
        *should_have_been_called_with_args,
        **should_have_been_called_with_kwargs
    )


def test_can_patch_instance_method():
    mock = Mock()
    mock.return_value = 'hello'
    p = Patched(orig=Greeter.hello, new=mock)
    try:
        Greeter.hello = p
        g = Greeter()
        assert 'hello' == g.hello('somebody')
    finally:
        Greeter.hello = Greeter.hello.orig


def test_can_patch_regular_method():
    mock = Mock()
    try:
        to_be_patched.nfoo = Patched(orig=to_be_patched.nfoo, new=mock)
        to_be_patched.nfoo(3)
    finally:
        to_be_patched.nfoo = to_be_patched.nfoo.orig

    assert mock.called
    mock.assert_called_once_with(to_be_patched.nfoo, 3)
