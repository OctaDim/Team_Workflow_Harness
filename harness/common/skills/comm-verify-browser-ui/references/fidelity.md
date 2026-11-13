# Browser-specific fidelity

Use cases relevant to the claim.

1. Textarea: model initial text/default value and current .value after edits,
   not a value attribute or permanently empty field.
2. Events: reproduce relevant dispatch lifetime; currentTarget becomes null after
   dispatch. Do not preserve it throughout an awaited fake handler or equate
   every await with dispatch completion. Exercise affected asynchronous paths.
3. Reachability: DOM element.click() does not prove user access. For pointer
   claims check visibility, scrolling, obstruction, intended target/allowed
   descendant and effect using suitable browser input; manual CDP coordinates
   are not mandatory.
4. Wiring: a helper unit test does not establish its UI call site. Use an
   interaction that reaches the real caller and observable result.
5. Measurement: execute the actual measurer. Lightweight tests may supply input
   geometry; browser-layout claims need real rendering. Stubbing the result hides
   defects in the measurer itself.
6. Containment: test content as well as container boundaries, including relevant
   overflow/clipping/scrolling and obstruction of neighboring controls. Judge
   against the contract; intentional popovers may extend beyond their parent.
