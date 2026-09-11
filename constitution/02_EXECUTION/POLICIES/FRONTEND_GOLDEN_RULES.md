# 17_FRONTEND_GOLDEN_RULES_MASTER_PROMPT.md

# FRONTEND GOLDEN RULES MASTER PROMPT

# THE CONSTITUTION OF CONSTITUTIONS

## PURPOSE

This document is the highest authority for all frontend engineering decisions.

It supersedes preferences.

It supersedes opinions.

It supersedes convenience.

It exists to ensure every system produced is:

- Secure
- Correct
- Reliable
- Maintainable
- Scalable
- Accessible
- Observable
- Performant
- Production Ready

Target Stack:

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- shadcn/ui
- Zod
- React Hook Form
- TanStack Query
- Supabase

---

# PART I — THE 25 ENGINEERING COMMANDMENTS

1. Correctness before speed.
2. Security before convenience.
3. Maintainability before cleverness.
4. Simplicity before abstraction.
5. Explicitness before magic.
6. Architecture before implementation.
7. Requirements before code.
8. Domains before components.
9. Contracts before integrations.
10. Validation before trust.
11. Ownership before sharing.
12. Accessibility before aesthetics.
13. Performance before optimization.
14. Observability before deployment.
15. Testing before release.
16. Reliability before velocity.
17. Governance before scale.
18. Boundaries before coupling.
19. Consistency before customization.
20. Documentation before dependency.
21. Review before merge.
22. Measure before optimize.
23. Automate before repeating.
24. Refactor before decay.
25. Production readiness before completion.

---

# PART II — ARCHITECTURE LAWS

26. Architecture is a business decision.

27. Every domain must have ownership.

28. Every feature must belong to a domain.

29. Pages compose domains.

30. Components do not own business rules.

31. Business logic belongs to domains.

32. Shared layers must remain generic.

33. Avoid god objects.

34. Avoid god services.

35. Avoid god components.

36. Modular monolith is the default.

37. Micro-frontends require strong justification.

38. Boundaries are more important than reuse.

39. Coupling is a liability.

40. Architecture must evolve safely.

---

# PART III — TYPESCRIPT LAWS

41. strict mode is mandatory.

42. any is forbidden.

43. ts-ignore is forbidden.

44. Public APIs must be typed.

45. Contracts must be typed.

46. Props must be typed.

47. Responses must be typed.

48. State must be typed.

49. Schemas must generate trust.

50. Type safety is non-negotiable.

---

# PART IV — SECURITY LAWS

51. Trust nothing.

52. Validate everything.

53. Input is hostile.

54. Output requires protection.

55. Secrets never reach the client.

56. Sessions must expire.

57. Permissions must be verified.

58. Authorization must be enforced.

59. RLS is mandatory.

60. Multi-tenant isolation is mandatory.

61. XSS prevention is required.

62. CSRF protection is required.

63. Secure defaults are mandatory.

64. Security reviews are required.

65. Security debt is production debt.

---

# PART V — STATE MANAGEMENT LAWS

66. Server state first.

67. URL state second.

68. Form state third.

69. Local state fourth.

70. Global state last.

71. State ownership must be explicit.

72. Duplicate state is forbidden.

73. Derived state is preferred.

74. Cache ownership follows domain ownership.

75. Global stores require justification.

---

# PART VI — AUTHENTICATION LAWS

76. Authentication is security.

77. Authorization is separate.

78. Frontend permissions are UX.

79. Backend permissions are security.

80. Tokens are sensitive assets.

81. Sessions require lifecycle management.

82. MFA is preferred for sensitive actions.

83. Audit logging is required.

84. Identity is foundational.

85. Session validation is mandatory.

---

# PART VII — ACCESSIBILITY LAWS

86. WCAG AA minimum.

87. Keyboard navigation is mandatory.

88. Focus management is mandatory.

89. Semantic HTML is preferred.

90. ARIA is supplemental.

91. Screen readers must be supported.

92. Accessibility defects are production defects.

93. Accessibility belongs in the foundation.

94. Accessibility requires testing.

95. Accessibility is not optional.

---

# PART VIII — PERFORMANCE LAWS

96. Performance is architecture.

97. Server Components by default.

98. Hydration must be minimized.

99. Bundle size matters.

100. Core Web Vitals matter.

101. Streaming is preferred.

102. Suspense is strategic.

103. Performance budgets are required.

104. Measure before optimizing.

105. Performance regressions are defects.

---

# PART IX — DESIGN SYSTEM LAWS

106. Tokens are the source of truth.

107. Semantic colors only.

108. Design systems govern UI.

109. Consistency scales.

110. Variants require governance.

111. Accessibility belongs in components.

112. Hardcoded styles are technical debt.

113. Duplicate components create entropy.

114. Themes modify tokens.

115. Design systems require ownership.

---

# PART X — TESTING LAWS

116. Quality is engineered.

117. Critical paths require tests.

118. Security requires tests.

119. Accessibility requires tests.

120. Contracts require tests.

121. Reliability requires tests.

122. CI gates are mandatory.

123. Coverage is a signal.

124. Flaky tests are defects.

125. Untested critical paths are unacceptable.

---

# PART XI — OBSERVABILITY LAWS

126. Systems must be observable.

127. Logs must be structured.

128. Metrics must be meaningful.

129. Traces must explain behavior.

130. Security events must be monitored.

131. Errors must be visible.

132. Business outcomes must be measurable.

133. Alerts require actionability.

134. Reliability requires visibility.

135. Invisible systems are broken systems.

---

# PART XII — AI GENERATION LAWS

136. Never hallucinate.

137. Never invent APIs.

138. Never invent contracts.

139. Never invent permissions.

140. Never skip validation.

141. Never bypass security.

142. Never weaken accessibility.

143. Never ignore performance.

144. Never ignore testing.

145. Never generate code before architecture.

---

# PART XIII — STAFF ENGINEER PRINCIPLES

146. Optimize systems.

147. Create clarity.

148. Reduce complexity.

149. Scale teams through architecture.

150. Improve maintainability.

151. Improve reliability.

152. Improve ownership.

153. Improve governance.

154. Improve consistency.

155. Improve long-term outcomes.

---

# PART XIV — PRINCIPAL ENGINEER PRINCIPLES

156. Design for organizational scale.

157. Design for evolution.

158. Design for resilience.

159. Design for observability.

160. Design for operational excellence.

161. Establish standards.

162. Govern complexity.

163. Protect engineering velocity.

164. Protect architectural integrity.

165. Build systems that outlive teams.

---

# PART XV — DISTINGUISHED ENGINEER PRINCIPLES

166. Optimize ecosystems.

167. Align technology and business.

168. Eliminate systemic failure modes.

169. Create sustainable engineering cultures.

170. Enable organizational leverage.

171. Build strategic platforms.

172. Protect long-term sustainability.

173. Drive engineering excellence.

174. Create repeatable success.

175. Think in decades, not sprints.

---

# FRONTEND EXCELLENCE FRAMEWORK

Every feature must satisfy:

✓ Correctness

✓ Security

✓ Reliability

✓ Accessibility

✓ Performance

✓ Observability

✓ Maintainability

✓ Scalability

✓ Testability

✓ Production Readiness

---

# ULTIMATE DEFINITION OF DONE

A feature is complete only when:

✓ Business requirements satisfied

✓ Architecture approved

✓ Domain ownership defined

✓ Contracts validated

✓ Security enforced

✓ Accessibility verified

✓ Performance validated

✓ Observability implemented

✓ Tests passing

✓ Documentation updated

✓ Review completed

✓ Production readiness confirmed

Anything less is incomplete.

---

# FINAL COMMANDMENT

Build systems.

Not pages.

Build architecture.

Not features.

Build products.

Not code.

Build organizations.

Not repositories.
