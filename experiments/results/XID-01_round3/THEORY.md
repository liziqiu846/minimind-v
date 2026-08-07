# XID-01 Round 3 Diagnostic-Mass Prediction Theorem

## Scope

This theorem gives a finite-class sufficient condition and a matching worst-case
sharpness construction under the stated information. It distinguishes population
identification margin from sample-count concentration. It does not provide a validated
way to estimate the separation parameters from a neural LVLM.

## Setup

Let \(\mathcal H\) be a finite conditional-predictor class, let
\(h^\star\in\mathcal H\) be an intended interaction rule, and define the target-bad set

\[
\mathcal B_\tau
=
\{h\in\mathcal H:
R_U(h)-R_U(h^\star)>\tau\}.
\]

Training examples are drawn from

\[
P_\lambda=(1-\lambda)P_0+\lambda Q,
\qquad 0\le\lambda\le1,
\]

where \(P_0\) is ordinary/base support and \(Q\) is an interaction-diagnostic
distribution.

Assume that for every \(h\in\mathcal B_\tau\),

\[
R_0(h)-R_0(h^\star)\ge-\beta
\tag{1}
\]

and

\[
R_Q(h)-R_Q(h^\star)\ge\gamma,
\tag{2}
\]

with \(\beta\ge0\) and \(\gamma>0\). Equation (1) permits ordinary support to favor a
shortcut by at most \(\beta\). Equation (2) requires diagnostic support to favor the
intended rule by at least \(\gamma\).

Let loss be bounded in \([0,B]\), and set

\[
\alpha_n(\delta)
=
B\sqrt{\frac{\log(2|\mathcal H|/\delta)}{2n}}.
\]

## Theorem 1: diagnostic-mass exclusion threshold

If

\[
\lambda\gamma-(1-\lambda)\beta>2\alpha_n(\delta),
\tag{3}
\]

then any empirical risk minimizer \(\widehat h\) trained on \(n\) IID samples from
\(P_\lambda\) satisfies

\[
R_U(\widehat h)-R_U(h^\star)\le\tau
\]

with probability at least \(1-\delta\).

When \(\beta+\gamma>0\), condition (3) is equivalent to

\[
\boxed{
\lambda>
\frac{\beta+2\alpha_n(\delta)}{\beta+\gamma}.
}
\tag{4}
\]

### Proof

For every target-bad \(h\), linearity of mixture risk and assumptions (1)–(2) give

\[
\begin{aligned}
R_\lambda(h)-R_\lambda(h^\star)
&=
(1-\lambda)[R_0(h)-R_0(h^\star)]\\
&\quad+\lambda[R_Q(h)-R_Q(h^\star)]\\
&\ge
\lambda\gamma-(1-\lambda)\beta.
\end{aligned}
\tag{5}
\]

As in round2, finite-class Hoeffding concentration implies, with probability at least
\(1-\delta\),

\[
\sup_{h\in\mathcal H}
|\widehat R_\lambda(h)-R_\lambda(h)|
\le\alpha_n.
\tag{6}
\]

On event (6), empirical ERM satisfies

\[
R_\lambda(\widehat h)-R_\lambda(h^\star)
\le2\alpha_n.
\tag{7}
\]

If \(\widehat h\in\mathcal B_\tau\), equations (3) and (5) would make the left side of
(7) strictly greater than \(2\alpha_n\), a contradiction. Therefore
\(\widehat h\notin\mathcal B_\tau\), proving the target-risk statement.

Finally,

\[
\lambda\gamma-(1-\lambda)\beta
=
\lambda(\gamma+\beta)-\beta,
\]

so (3) is equivalent to (4). \(\square\)

## Proposition 2: worst-case sharpness under the stated information

Suppose

\[
m=\lambda\gamma-(1-\lambda)\beta\le2\alpha
\]

and \(|m|\le1/2,\alpha\le1/4\). Under only assumptions (1)–(2) and a uniform-deviation
event of radius \(\alpha\), there exists a bounded two-rule risk realization in which a
target-bad rule is an empirical minimizer.

### Proof

Choose the extremal allowed gaps

\[
R_0(h)-R_0(h^\star)=-\beta,
\qquad
R_Q(h)-R_Q(h^\star)=\gamma,
\]

so the mixture population gap is exactly \(m\). Set

\[
R_\lambda(h^\star)=\frac12-\frac m2,
\qquad
R_\lambda(h)=\frac12+\frac m2.
\]

The assumed ranges keep both population risks in \([0,1]\). Choose empirical risks

\[
\widehat R_\lambda(h^\star)=R_\lambda(h^\star)+\alpha,
\qquad
\widehat R_\lambda(h)=R_\lambda(h)-\alpha.
\]

They also lie in \([0,1]\), each differs from its population risk by at most
\(\alpha\), and

\[
\widehat R_\lambda(h)-\widehat R_\lambda(h^\star)
=m-2\alpha\le0.
\]

Thus the bad rule ties or beats the intended rule while the uniform-deviation event
holds. No universally smaller threshold follows from only \(\beta,\gamma,\alpha\).
\(\square\)

This proposition establishes worst-case sharpness, not necessity in a particular
optimization problem. Extra structure or favorable tie-breaking can succeed below the
threshold.

## Corollary 1: sample count cannot create a missing identification margin

If the added support is observationally redundant for some target-bad rule, then its
diagnostic separation for that rule is \(\gamma=0\). With \(\beta=0\), the population
gap remains zero for every \(\lambda\). Increasing \(n\) sends \(\alpha_n\) toward zero
but never makes the strict condition \(0>2\alpha_n\) true. Repetition reduces estimation
uncertainty; it does not eliminate an exact shortcut tie.

If \(\beta>0\), even the infinite-sample limit requires

\[
\lambda>\frac{\beta}{\beta+\gamma}.
\]

Thus some positive diagnostic mass is asymptotically necessary for this worst-case
guarantee when base support favors the shortcut.

## Round1 specialization

In the identifying four-observation construction:

- ordinary cells tie the two rules, so \(\beta=0\);
- one of four cells is diagnostic, so \(\lambda=1/4\);
- diagnostic NLL separation is
  \[
  \gamma=\log\frac{1-\eta}{\eta};
  \]
- in the population table \(\alpha=0\).

The theorem's source gap is therefore

\[
\lambda\gamma
=
\frac14\log\frac{1-\eta}{\eta},
\]

exactly the round1 unique-minimizer gap. In redundant support, the two rules agree on
every observed cell, so \(\gamma=0\) and no strict identification guarantee follows.

## New falsifiable consequences

The theorem yields three directional consequences before any real-model outcome is
examined:

1. At fixed diagnostic quality \(\gamma\) and base bias \(\beta\), larger \(n\) lowers
   the minimum diagnostic mass only through \(\alpha_n\).
2. At large \(n\), redundant data cannot replace diagnostic mass when
   \(\beta>0\); the threshold approaches \(\beta/(\beta+\gamma)\), not zero.
3. Improving diagnostic quality \(\gamma\) or reducing base shortcut advantage
   \(\beta\) lowers the required mass, suggesting two distinct algorithmic levers:
   construct more discriminating cross-modal examples or reduce shortcut-favoring
   ordinary supervision.

## Inference boundary

- \(\beta\) and \(\gamma\) are population NLL gaps over predeclared rule sets. No existing
  checkpoint proxy has been shown to estimate them.
- The bad set uses target risk and cannot be selected repeatedly on final confirmation.
- The theorem assumes the intended rule is in \(\mathcal H\); approximation error remains
  separate.
- Finite-class concentration is not a neural-network complexity theorem.
- A real mechanism-intervention training test must independently construct conditions
  that change diagnostic separation/mass while holding pixels, labels, target format,
  compute and ordinary support fixed. Without that isolation, method gains would not
  validate this theorem.
