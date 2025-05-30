# Technical Review Examples

This document provides examples of how to use the Technical Leader Review System for different types of projects and scenarios.

## Example 1: New Feature Review 🚀

### Scenario
Reviewing a new user authentication feature before production deployment.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @auth/login.tsx @auth/register.tsx @services/auth-api.ts @hooks/useAuth.ts
Focus on: security, error handling, user experience
```

### Expected Review Focus
- Security vulnerabilities in authentication flow
- Input validation and sanitization
- Error handling and user feedback
- Integration with existing authentication system
- Code quality and maintainability

### Key Review Sections
- **Security Assessment:** Authentication best practices, token handling, password security
- **Quick Wins:** Add loading states, improve error messages, implement form validation
- **Architecture Review:** Integration patterns with existing auth system

---

## Example 2: Legacy Code Refactoring 🔧

### Scenario
Evaluating a legacy jQuery component for React migration.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @legacy/user-dashboard.js @legacy/user-dashboard.css @proposed/UserDashboard.tsx
Focus on: modernization strategy, technical debt reduction, performance improvements
```

### Expected Review Focus
- Technical debt assessment and prioritization
- Migration strategy and approach
- Performance improvements from modernization
- Code quality improvements
- Risk assessment for the migration

### Key Review Sections
- **Technical Debt Analysis:** Identification of legacy patterns and issues
- **Migration Roadmap:** Phased approach for React conversion
- **Risk Mitigation:** Strategies for safe legacy code replacement

---

## Example 3: Performance Optimization Review ⚡

### Scenario
Reviewing a React application with performance issues.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @components/ProductList.tsx @components/ProductCard.tsx @hooks/useProducts.ts @utils/api.ts
Focus on: performance optimization, rendering efficiency, memory usage
```

### Expected Review Focus
- React rendering performance issues
- Memory leaks and unnecessary re-renders
- API call optimization
- Bundle size and loading performance
- Code splitting opportunities

### Key Review Sections
- **Performance Bottlenecks:** Identification of slow components and operations
- **Quick Wins:** Memoization, lazy loading, component optimization
- **Long-term Strategy:** Architecture changes for better performance

---

## Example 4: API Design Review 🌐

### Scenario
Reviewing a new REST API before implementation.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @api/routes/users.ts @api/models/User.ts @api/middleware/auth.ts @api/controllers/UserController.ts
Focus on: API design patterns, scalability, security, documentation
```

### Expected Review Focus
- RESTful API design principles
- Data validation and sanitization
- Authentication and authorization
- Error handling and response formatting
- API documentation and testing

### Key Review Sections
- **API Design Patterns:** REST conventions, resource naming, HTTP methods
- **Security Review:** Authentication, authorization, data protection
- **Scalability Considerations:** Database design, caching, rate limiting

---

## Example 5: Full-Stack Feature Review 🏗️

### Scenario
Comprehensive review of a complete feature spanning frontend and backend.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @frontend/OrderForm.tsx @backend/orders/controller.ts @backend/orders/model.ts @shared/types.ts
Focus on: end-to-end architecture, data consistency, user experience, maintainability
```

### Expected Review Focus
- Frontend-backend integration patterns
- Data flow and state management
- Type safety across the stack
- Error handling end-to-end
- Testing strategy for full feature

### Key Review Sections
- **Architecture Review:** Full-stack patterns and integration
- **Data Consistency:** Type safety and validation across layers
- **User Experience:** Error handling, loading states, feedback

---

## Example 6: Security-Focused Review 🔒

### Scenario
Security audit of a payment processing feature.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @payments/PaymentForm.tsx @payments/payment-service.ts @payments/webhook-handler.ts
Focus on: security vulnerabilities, data protection, compliance, audit trail
```

### Expected Review Focus
- PCI DSS compliance considerations
- Data encryption and secure transmission
- Input validation and sanitization
- Audit logging and monitoring
- Error handling without information leakage

### Key Review Sections
- **Security Vulnerabilities:** Comprehensive security assessment
- **Compliance Review:** Industry standard compliance (PCI DSS, GDPR)
- **Risk Assessment:** Security risks and mitigation strategies

---

## Example 7: Testing Strategy Review 🧪

### Scenario
Evaluating testing coverage and strategy for a complex component.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @components/DataTable.tsx @components/DataTable.test.tsx @utils/table-helpers.ts @utils/table-helpers.test.ts
Focus on: test coverage, testing strategy, maintainable tests, edge cases
```

### Expected Review Focus
- Test coverage completeness
- Test quality and maintainability
- Edge case coverage
- Integration vs unit testing strategy
- Mock usage and test isolation

### Key Review Sections
- **Testing Strategy:** Comprehensive approach to testing
- **Test Quality:** Maintainable and meaningful tests
- **Coverage Analysis:** Gaps in test coverage and edge cases

---

## Example 8: Database Design Review 📊

### Scenario
Reviewing database schema and query optimization.

### Command Usage
```
Use @technical-leader-review.mdc
Review these files: @database/migrations/001-create-users.sql @models/User.ts @repositories/UserRepository.ts
Focus on: database design, query performance, data integrity, scalability
```

### Expected Review Focus
- Database schema design and normalization
- Query performance and indexing
- Data integrity constraints
- Scalability considerations
- ORM usage patterns

### Key Review Sections
- **Database Design:** Schema optimization and relationships
- **Performance Review:** Query optimization and indexing strategy
- **Scalability Planning:** Growth considerations and optimization

---

## Tips for Effective Reviews 💡

### 1. Be Specific About Focus Areas
Instead of a general review, specify what aspects you want to emphasize:
- `Focus on: security, performance`
- `Focus on: code quality, maintainability`
- `Focus on: architecture, scalability`

### 2. Include Context Files
Reference related files that provide context:
```
Review these files: @main-component.tsx @related-service.ts @types.ts
Context files: @README.md @docs/architecture.md
```

### 3. Specify Review Depth
Indicate whether you want a quick scan or comprehensive review:
- `Quick architectural review focusing on design patterns`
- `Comprehensive security audit with detailed recommendations`
- `Performance review with specific optimization suggestions`

### 4. Use for Different Stages
- **Pre-implementation:** Review designs and architecture plans
- **Mid-development:** Check progress and identify issues early
- **Pre-deployment:** Final quality and security assessment
- **Post-deployment:** Retrospective analysis and improvement planning

### 5. Follow Up on Recommendations
Use the generated implementation roadmap to:
- Track progress on recommended improvements
- Schedule follow-up reviews
- Measure success metrics
- Share learnings with the team

---

*These examples demonstrate the flexibility and power of the Technical Leader Review System. Adapt the focus areas and file selections to match your specific needs and project context.* 