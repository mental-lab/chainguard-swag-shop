# GitLab Duo Chat Rules

## Project Purpose

Demonstrate GitLab Duo Platform features in 60-minute presentations

## Architecture Understanding

### Core Application Stack

- **Backend**: Flask 3.0.3 with session-based cart management
- **Database**: Hardcoded product catalog in `db.py` (SQLite schema defined but unused)
- **Frontend**: Jinja2 templates with responsive GitLab-branded design
- **Deployment**: Dual model - dynamic Flask app + static GitLab Pages generation

### Key Files and Their Purpose

- `app.py`: Main Flask application with all routes and business logic
- `db.py`: Product catalog (18 GitLab merchandise items) and database models
- `freezer.py`: Flask-Frozen static site generator for GitLab Pages

## Development Standards

### Code Style and Quality

- Follow Python PEP 8 standards
- Use Flask best practices for route organization
- Maintain Jinja2 template inheritance (all extend `base.html`)
- Keep hardcoded secret keys only for demo purposes
- No real payment processing - demo checkout only

### Testing Requirements

- Unit tests in `tests/test.py` focus on product model validation
- Test both dynamic Flask functionality and static generation compatibility

### CI/CD Pipeline Standards

- Use emoji-based stage names: 🛠 build, ❄️ Security, 🚂 test, ⚙️ Run, 🐍 deploy, 🛑 Stop, 📚 cleanup
- Include comprehensive security scanning (dependency, secret detection, SAST)
- Maintain Flake8 code quality checks
- Support merge request review apps with path prefixes
- Use modern `rules` syntax instead of deprecated `only`

## Flask-Specific Guidance

### Route Conventions

- All routes use `.html` extensions for Flask-Frozen compatibility
- Session-based cart storage (not database-persisted)
- POST routes for cart modifications will fail during static generation (expected behavior)
- Shopping cart lives entirely in Flask sessions, orders are not stored

### Static Generation Limitations

- Flask-Frozen fails on POST-only routes (`/add_to_cart.html`) - this is expected
- CI pipeline uses `|| true` workaround for freezer errors
- Only GET routes work with static site generation
- Static files go to `build/` then move to `public/` for GitLab Pages

### Container Optimization

- Exclude documentation, runbooks, and development files from Docker images
- Use `.dockerignore` to minimize image size
- Maintain port 8000 for Flask development server
- **Critical**: Always include port forwarding (`-p 8000:8000`) in Docker run commands

### Development Workflow

- Use Makefile shortcuts: `make help`, `make install`, `make develop`, `make static`, `make runtime`
- Virtual environment in `.venv/` (not `venv/`)
- Python 3.11+ compatibility
- Support both local development and containerized deployment

## Code Review Requirements

### Approval Process

- Follow conventional commit message format
- Include demo-related changes in commit descriptions

### Security Considerations

- Hardcoded secret keys acceptable for demo purposes only
- No real customer data storage or processing
- External image hosting via brilliantmade.com CDN
- Session security adequate for demonstration use

## GitLab Platform Features to Highlight

### Security and Compliance

- Dependency scanning with debug logging
- Secret detection across codebase
- SAST with advanced and experimental features enabled
- Code quality integration with detailed reporting

## Common Tasks and Guidance

### When Adding New Features

- Ensure Flask routes work in both dynamic and static modes
- Add appropriate tests to maintain coverage
- Update documentation in RunBooks/ if demo-relevant
- Consider impact on 60-minute demo flow

### When Modifying CI/CD

- Maintain emoji-based stage naming convention
- Keep security scanning components up to date
- Test both main branch and merge request pipelines
- Ensure static site generation still works (with expected failures)

### When Updating Dependencies

- Test with both Python 3.11+ environments
- Verify Flask-Frozen compatibility
- Update requirements.txt and test in clean virtual environment
- Check Docker image build process

This project serves as a comprehensive showcase of GitLab's development platform capabilities while maintaining a functional, understandable Flask application structure.
