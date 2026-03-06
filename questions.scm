(define (caar x) (car (car x)))
(define (cadr x) (car (cdr x)))
(define (cadar x) (car (cdr (car x))))
(define (cdar x) (cdr (car x)))
(define (cddr x) (cdr (cdr x)))


(define (enumerate s)
  (define (helper lst index acc)
    (if (null? lst)
        acc
        (helper (cdr lst)
                (+ index 1)
                (append acc (list (list index (car lst)))))))
  (helper s 0 '()))


(define (get dict key)
  (if(null? dict)
  #f
  (if (equal? key (caar dict))
  (cadar dict)
  (get(cdr dict) key)
  )
  )
  )


(define (set dict key val)

  (if (null? dict)
      (list (list key val))
      (if (equal? key (caar dict))
          (cons (list key val) (cdr dict)) 
          (cons (car dict) (set (cdr dict) key val))))) 





(define (solution-code problem solution)
  (define (replace-blanks expr)
    (cond
      ((null? expr) '())                   
      ((eq? expr '_____ ) solution)        
      ((pair? expr)                        
       (cons (replace-blanks (car expr))
             (replace-blanks (cdr expr))))
      (else expr)))                        
  (replace-blanks problem))

