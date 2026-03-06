import sys

from link import *
from scheme_utils import *
from scheme_reader import read_line
from scheme_builtins import create_global_frame
from ucb import main, trace

##############
# Eval/Apply #
##############

def scheme_eval(expr, env, _=None): # Optional third argument is ignored
    """Evaluate Scheme expression EXPR in Frame ENV.

    >>> expr = read_line('(+ 2 2)')
    >>> expr
    Link('+', Link(2, Link(2)))
    >>> scheme_eval(expr, create_global_frame())
    4
    """
    # Evaluate atoms
    if scheme_symbolp(expr):
        return env.lookup(expr)
    elif self_evaluating(expr):
        return expr

    # All non-atomic expressions are lists (combinations)
    if not scheme_listp(expr):
        raise SchemeError('malformed list: {0}'.format(repl_str(expr)))
    first, rest = expr.first, expr.rest

    from scheme_forms import SPECIAL_FORMS # Import here to avoid a cycle when modules are loaded
    if scheme_symbolp(first) and first in SPECIAL_FORMS:
        return SPECIAL_FORMS[first](rest, env)
    else:
        procedure=scheme_eval(first,env)
        args=nil
        tail=None
        current=rest
        while current is not nil:
            evaluated=scheme_eval(current.first, env)
            new_node=Link(evaluated,nil)
            if args is nil:
                args= new_node
                tail=new_node
            else:
                tail.rest=new_node
                tail=new_node
            current=current.rest
        return scheme_apply(procedure,args,env)

def scheme_apply(procedure, args, env):
    """Apply Scheme PROCEDURE to argument values ARGS (a Scheme list) in
    Frame ENV, the current environment."""
    validate_procedure(procedure)
    if not isinstance(env, Frame):
       assert False, "Not a Frame: {}".format(env)
    if isinstance(procedure, BuiltinProcedure):
        py_args=[]
        while args is not nil:
            py_args.append(args.first)
            args=args.rest

        if procedure.need_env:
            py_args.append(env)
        try:
            return procedure.py_func(*py_args)
        except TypeError as err:
            raise SchemeError('incorrect number of arguments: {0}'.format(procedure))
    elif isinstance(procedure, LambdaProcedure):
        new_frame= procedure.env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, new_frame)
    elif isinstance(procedure, MuProcedure):
        new_frame= env.make_child_frame(procedure.formals, args)
        return eval_all(procedure.body, new_frame)
    else:
        assert False, "Unexpected procedure: {}".format(procedure)

def eval_all(expressions, env):
    if expressions is nil:
        return None
    result=None
    while expressions is not nil:
        result= scheme_eval(expressions.first, env)
        expressions=expressions.rest
    return result

