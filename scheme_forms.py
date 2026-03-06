from scheme_eval_apply import *
from scheme_utils import *
from scheme_classes import *
from scheme_builtins import *

#################
# Special Forms #
#################

def do_define_form(expressions, env):
    validate_form(expressions, 2) # Checks that expressions is a list of length at least 2
    signature = expressions.first
    if scheme_symbolp(signature):
        # assigning a name to a value e.g. (define x (+ 1 2))
        validate_form(expressions, 2, 2) # Checks that expressions is a list of length exactly 2
        value=scheme_eval(expressions.rest.first, env)
        env.define(signature,value)
        return signature
    
    elif isinstance(signature, Link) and scheme_symbolp(signature.first):
        name=signature.first
        formals= signature.rest
        body=expressions.rest
        procedure= do_lambda_form(Link(formals, body), env)
        env.define(name,procedure)
        return name
    else:
        bad_signature = signature.first if isinstance(signature, Link) else signature
        raise SchemeError('non-symbol: {0}'.format(bad_signature))

def do_quote_form(expressions, env):
    validate_form(expressions, 1, 1)
    return expressions.first

def do_begin_form(expressions, env):
    validate_form(expressions, 1)
    return eval_all(expressions, env)

def do_lambda_form(expressions, env):
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    body= expressions.rest
    return LambdaProcedure(formals, body, env)

def do_if_form(expressions, env):
    validate_form(expressions, 2, 3)
    if is_scheme_true(scheme_eval(expressions.first, env)):
        return scheme_eval(expressions.rest.first, env)
    elif len_link(expressions) == 3:
        return scheme_eval(expressions.rest.rest.first, env)

def do_and_form(expressions, env):
    if expressions is nil:
        return True
    result=True
    while expressions is not nil:
        result=scheme_eval(expressions.first, env)
        if not is_scheme_true(result):
            return result
        expressions=expressions.rest
    return result

def do_or_form(expressions, env):
    if expressions is nil:
        return False
    result=False
    while expressions is not nil:
        result= scheme_eval(expressions.first, env)
        if is_scheme_true(result):
            return result
        expressions=expressions.rest
    return result

def do_cond_form(expressions, env):
 
    while expressions is not nil:
        clause = expressions.first
        validate_form(clause, 1)
        if clause.first == 'else':
            test = True
            if expressions.rest != nil:
                raise SchemeError('else must be last')
        else:
            test = scheme_eval(clause.first, env)
        if is_scheme_true(test):
            if clause.rest is nil:
                return test
            else:
                return eval_all(clause.rest, env)
            
        expressions = expressions.rest

def do_let_form(expressions, env):
    validate_form(expressions, 2)
    let_env = make_let_frame(expressions.first, env)
    return eval_all(expressions.rest, let_env)

def make_let_frame(bindings, env):
    if not scheme_listp(bindings):
        raise SchemeError('bad bindings list in let form')
    names = vals = nil
    for binding in bindings:
        validate_form(binding, 2, 2)
        name=binding.first
        val=scheme_eval(binding.rest.first, env)
        names= Pair(name, names)
        vals= Pair(val,vals)
    names=list_to_scheme_list(reversed(scheme_list_to_python_list(names)))
    vals= list_to_scheme_list(reversed(scheme_list_to_python_list(vals)))
    return env.make_child_frame(names, vals)



def do_quasiquote_form(expressions, env):
    def quasiquote_item(val, env, level):
        if not scheme_pairp(val):
            return val
        if val.first == 'unquote':
            level -= 1
            if level == 0:
                expressions = val.rest
                validate_form(expressions, 1, 1)
                return scheme_eval(expressions.first, env)
        elif val.first == 'quasiquote':
            level += 1

        return map_link(lambda elem: quasiquote_item(elem, env, level), val)

    validate_form(expressions, 1, 1)
    return quasiquote_item(expressions.first, env, 1)

def do_unquote(expressions, env):
    raise SchemeError('unquote outside of quasiquote')




def do_mu_form(expressions, env):
    """Evaluate a mu form."""
    validate_form(expressions, 2)
    formals = expressions.first
    validate_formals(formals)
    body=expressions.rest
    return MuProcedure(formals,body)



SPECIAL_FORMS = {
    'and': do_and_form,
    'begin': do_begin_form,
    'cond': do_cond_form,
    'define': do_define_form,
    'if': do_if_form,
    'lambda': do_lambda_form,
    'let': do_let_form,
    'or': do_or_form,
    'quote': do_quote_form,
    'quasiquote': do_quasiquote_form,
    'unquote': do_unquote,
    'mu': do_mu_form,
}