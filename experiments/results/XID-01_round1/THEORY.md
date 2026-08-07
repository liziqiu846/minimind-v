# XID-01 Round 1 Finite Theory

## Scope

This note proves a finite, task-specific proposition. `PROVEN` below means proven only
for the stated two-rule hypothesis class and support tables. It is not a theorem about
neural LVLMs, SGD, or natural multimodal data.

## Definition 1: observed-support near-minimizer set

Let \(\mathcal H\) be a conditional next-token predictor class, \(P_S\) an observed
training distribution, and \(R_S(h)\) its expected next-token NLL. For
\(\epsilon\ge 0\), define

\[
\mathcal E_\epsilon(P_S)
=
\left\{
h\in\mathcal H:
R_S(h)\le \inf_{g\in\mathcal H}R_S(g)+\epsilon
\right\}.
\]

This is an NLL-relative equivalence set, not a claim that its members have identical
parameters or representations.

## Definition 2: target interaction diameter

For a target distribution \(P_U\), define

\[
\operatorname{Diam}_U(\mathcal E_\epsilon)
=
\sup_{h,g\in\mathcal E_\epsilon}
\left|R_U(h)-R_U(g)\right|.
\]

Large diameter means observed-support near-minimization leaves rules with materially
different target risk unresolved. The object is formal in this finite problem; it has
not been validated as an empirical checkpoint statistic.

## Construction

Let \(V\in\{0,1\}\), \(L\in\{a,b,c\}\), and \(Y\in\{0,1\}\). A shared structural
parameter \(\theta\in\{0,1\}\) controls two cross-modal cells:

\[
f_\theta(v,l)
=
\begin{cases}
\theta,&(v,l)\in D=\{(0,b),(1,c)\},\\
0,&\text{otherwise}.
\end{cases}
\]

The conditional predictor \(h_\theta\) assigns probability \(1-\eta\) to
\(f_\theta(v,l)\) and probability \(\eta\) to the other token, where
\(0<\eta<1/2\). Thus \(\theta=0\) is a constant-token shortcut, while
\(\theta=1\) activates one shared cross-modal rule at both a diagnostic and a target
combination.

The redundant and identifying multisets are

\[
S_R=[(0,a),(1,b),(0,c),(1,a)]
\]

and

\[
S_I=[(0,b),(1,a),(0,c),(1,a)].
\]

Both have four observations, visual counts \((2,2)\), and language counts
\((a:2,b:1,c:1)\). The target \(U=\{(1,c)\}\) is absent from both, while the individual
values \(V=1\) and \(L=c\) occur in both.

## Proposition 1: matched marginals do not imply rule identification

For the construction above:

1. Under \(S_R\), the complete labelled training distribution is identical for
   \(\theta=0\) and \(\theta=1\), and
   \(\mathcal E_0(P_R)=\{h_0,h_1\}\).
2. Any possibly randomized learner that observes only the redundant labelled sample has
   worst-case target 0–1 error at least \(1/2\) over
   \(\theta\in\{0,1\}\).
3. Under \(S_I\), the ground-truth \(h_\theta\) is the unique NLL minimizer in
   \(\mathcal H=\{h_0,h_1\}\). The wrong rule has excess NLL
   \[
   \Delta_I(\eta)
   =
   \frac14\log\frac{1-\eta}{\eta}>0.
   \]
4. The unique identifying-support minimizer predicts the correct argmax token on the
   unseen target \((1,c)\).
5. For either fixed ground-truth world, the redundant exact-minimizer target-NLL
   diameter is
   \[
   \operatorname{Diam}_U(\mathcal E_0(P_R))
   =
   \log\frac{1-\eta}{\eta},
   \]
   whereas the identifying exact-minimizer diameter is zero.

### Proof

Every cell in \(S_R\) lies outside \(D\). Hence
\(f_0(v,l)=f_1(v,l)=0\) on the entire redundant support. The labelled observations and
the two predictors' token probabilities are identical there, so both have the same NLL
and both belong to \(\mathcal E_0(P_R)\).

Because the redundant labelled sample has the same distribution in both worlds, a
learner must have the same target prediction distribution in both. Let \(q\) be its
probability of predicting token 1 at \((1,c)\). The target errors are \(q\) when
\(\theta=0\) and \(1-q\) when \(\theta=1\). Therefore

\[
\max\{q,1-q\}\ge \frac12,
\]

with equality only at \(q=1/2\).

The identifying support contains the diagnostic cell \((0,b)\in D\) exactly once.
At the other three observations, \(h_0\) and \(h_1\) make the same prediction. The
ground-truth predictor assigns the observed diagnostic token probability \(1-\eta\);
the wrong predictor assigns it \(\eta\). Consequently the wrong predictor's excess
average NLL is

\[
\frac14[-\log\eta+\log(1-\eta)]
=
\frac14\log\frac{1-\eta}{\eta}>0,
\]

so the ground-truth predictor is the unique minimizer.

The same parameter \(\theta\), rather than an independent target lookup value, controls
both \((0,b)\) and the unseen \((1,c)\). Recovering \(\theta\) from the diagnostic cell
therefore gives the correct target argmax. Finally, at the target one hypothesis assigns
the ground-truth token probability \(1-\eta\) and the other assigns \(\eta\), so their
NLL difference is \(\log((1-\eta)/\eta)\). A singleton exact-minimizer set has diameter
zero. \(\square\)

## What is scientifically new in the construction

The result is not “more data helps”: both designs have the same number of observations.
It is not “marginal diversity helps”: the visual and language marginals are exactly
matched. It is not “the target cell was leaked”: the target combination is absent from
both designs. Transfer is possible only because a diagnostic cross-modal cell and the
unseen target share a structural interaction parameter.

This is the smallest formal example found in this round of an
**interaction-identifying support** distinction under next-token NLL.

## What remains ordinary or unresolved

- The minimax half-error statement is an indistinguishability argument adjacent to
  standard no-free-lunch results. Its VLM-specific content comes from the matched
  modality marginals and the shared cross-modal parameter, not from a new universal
  impossibility technique.
- The hypothesis class is supplied and contains the correct structural rule. Neural
  networks may contain many additional shortcuts and approximations.
- Unique population/empirical ERM in this deterministic table does not prove SGD selects
  the intended rule.
- Natural LVLM next-token sequences have stochastic labels, multiple positions,
  overlapping concepts and representation error.
- No local MiniMind-V experiment has yet shown that a real support intervention changes
  the proposed equivalence class or unseen risk.

The next theoretical step must therefore add approximation/estimation terms and state a
general target-risk decomposition or bound. Repeating this table with more cells would
not add scientific evidence.
