# Emergency Procedures and Rollback Guide

## Table of Contents
1. [Emergency Response Overview](#emergency-response-overview)
2. [Incident Classification](#incident-classification)
3. [Immediate Response Procedures](#immediate-response-procedures)
4. [Rollback Procedures](#rollback-procedures)
5. [Data Recovery](#data-recovery)
6. [System Restoration](#system-restoration)
7. [Communication Protocols](#communication-protocols)
8. [Post-Incident Analysis](#post-incident-analysis)
9. [Prevention Measures](#prevention-measures)

## Emergency Response Overview

### Emergency Contact Information
- **Technical Lead**: [Name] - [Phone] - [Email]
- **System Administrator**: [Name] - [Phone] - [Email]
- **Business Owner**: [Name] - [Phone] - [Email]
- **Hosting Provider**: [Provider] - [Support Phone] - [Support Email]

### Response Team Roles
- **Incident Commander**: Coordinates response, makes decisions
- **Technical Lead**: Handles technical resolution
- **Communications Lead**: Manages stakeholder communication
- **Business Representative**: Assesses business impact

## Incident Classification

### Severity Levels

#### Critical (P0) - Immediate Response Required
- **Definition**: Complete system outage, data loss, security breach
- **Response Time**: 15 minutes
- **Examples**:
  - Web store completely inaccessible
  - Desktop application won't start
  - Data corruption detected
  - Security breach confirmed

#### High (P1) - Urgent Response Required
- **Definition**: Major functionality impaired, significant user impact
- **Response Time**: 1 hour
- **Examples**:
  - Search functionality broken
  - Shopping cart not working
  - Product images not loading
  - Synchronization failures

#### Medium (P2) - Standard Response
- **Definition**: Minor functionality issues, limited user impact
- **Response Time**: 4 hours
- **Examples**:
  - Slow page loading
  - Minor UI glitches
  - Non-critical features unavailable

#### Low (P3) - Planned Response
- **Definition**: Cosmetic issues, enhancement requests
- **Response Time**: 24 hours
- **Examples**:
  - Styling inconsistencies
  - Feature requests
  - Documentation updates

## Immediate Response Procedures

### Step 1: Incident Detection and Assessment (0-5 minutes)

#### Detection Methods
- **Automated Monitoring**: System alerts, error logs
- **User Reports**: Customer complaints, support tickets
- **Internal Discovery**: Team member identification

#### Initial Assessment Checklist
- [ ] Confirm incident is real and not false alarm
- [ ] Determine severity level (P0-P3)
- [ ] Identify affected systems and users
- [ ] Estimate business impact
- [ ] Document initial findings

### Step 2: Incident Response Activation (5-15 minutes)

#### For Critical (P0) Incidents
1. **Immediately notify Incident Commander**
2. **Activate emergency response team**
3. **Create incident war room (physical or virtual)**
4. **Begin incident log documentation**
5. **Assess need for immediate rollback**

#### For High (P1) Incidents
1. **Notify Technical Lead**
2. **Create incident ticket**
3. **Begin troubleshooting**
4. **Prepare rollback if needed**

### Step 3: Initial Stabilization (15-30 minutes)

#### Quick Fixes to Try First
```bash
# Web Store Issues
# 1. Clear browser cache and reload
# 2. Check service worker status
# 3. Verify JSON data integrity
# 4. Restart web server if applicable

# Desktop Application Issues
# 1. Restart application
# 2. Check Python dependencies
# 3. Verify file permissions
# 4. Check Git connectivity

# Data Synchronization Issues
# 1. Check internet connectivity
# 2. Verify Git repository status
# 3. Check for file locks
# 4. Validate JSON structure
```

## Rollback Procedures

### Automated Rollback

#### Using Deployment Script
```bash
# Quick rollback to previous version
python scripts/deploy.py rollback

# Rollback to specific backup
python scripts/deploy.py rollback --backup backup_20231201_120000

# Verify rollback success
python scripts/deploy.py test
```

#### Web Store Rollback
```bash
# 1. Stop web server (if applicable)
sudo systemctl stop nginx  # or apache2

# 2. Backup current state
cp -r /var/www/html /var/www/html_backup_$(date +%Y%m%d_%H%M%S)

# 3. Restore from backup
cp -r /path/to/backup/html/* /var/www/html/

# 4. Restart web server
sudo systemctl start nginx

# 5. Verify functionality
curl -I http://your-domain.com
```

### Manual Rollback Procedures

#### Desktop Application Rollback
```bash
# 1. Stop desktop application
# (Close all instances)

# 2. Backup current files
mkdir backup_$(date +%Y%m%d_%H%M%S)
cp *.py backup_$(date +%Y%m%d_%H%M%S)/
cp -r Programa backup_$(date +%Y%m%d_%H%M%S)/

# 3. Restore from Git
git checkout HEAD~1  # Go back one commit
# or
git checkout <specific-commit-hash>

# 4. Restore data files if needed
cp backups/latest_backup.json html/JS/productos.json

# 5. Test application
python customtk.py
```

#### Database/JSON Rollback
```bash
# 1. Stop all applications accessing data
# 2. Backup current data
cp html/JS/productos.json html/JS/productos_backup_$(date +%Y%m%d_%H%M%S).json
cp html/JS/historial.json html/JS/historial_backup_$(date +%Y%m%d_%H%M%S).json

# 3. Restore from backup
cp backups/backup_YYYYMMDD_HHMMSS.json html/JS/productos.json

# 4. Validate data integrity
python -c "import json; json.load(open('html/JS/productos.json'))"

# 5. Restart applications
```

### Rollback Verification Checklist

After any rollback, verify:
- [ ] Web store loads correctly
- [ ] Desktop application starts
- [ ] Product data displays properly
- [ ] Search functionality works
- [ ] Shopping cart functions
- [ ] Data synchronization works
- [ ] No error messages in logs
- [ ] Performance is acceptable

## Data Recovery

### Data Loss Scenarios

#### Scenario 1: Corrupted JSON Files
```bash
# 1. Stop all applications
# 2. Assess corruption extent
python -c "
import json
try:
    with open('html/JS/productos.json') as f:
        data = json.load(f)
    print('JSON is valid')
except Exception as e:
    print(f'JSON corruption: {e}')
"

# 3. Restore from backup
cp backups/latest_good_backup.json html/JS/productos.json

# 4. Verify restoration
python -c "import json; print(len(json.load(open('html/JS/productos.json'))))"
```

#### Scenario 2: Git Repository Issues
```bash
# 1. Check repository status
git status
git log --oneline -10

# 2. If repository is corrupted
git fsck --full

# 3. Restore from remote
git fetch origin
git reset --hard origin/main

# 4. If remote is also corrupted, restore from backup
rm -rf .git
git init
git remote add origin <repository-url>
# Restore files from backup
# Commit and push
```

#### Scenario 3: Complete Data Loss
```bash
# 1. Stop all systems
# 2. Assess available backups
ls -la backups/

# 3. Choose most recent valid backup
# 4. Restore all data files
cp backups/backup_YYYYMMDD_HHMMSS.json html/JS/productos.json
cp backups/historial_YYYYMMDD_HHMMSS.json html/JS/historial.json

# 5. Restore images if needed
cp -r backups/img_backup/* html/img/

# 6. Reinitialize Git if needed
git init
git add .
git commit -m "Restore from backup after data loss"
git push origin main
```

### Data Validation After Recovery

```python
# data_validator.py
import json
import os
from datetime import datetime

def validate_products_data(file_path):
    """Validate products JSON structure"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        if not isinstance(products, list):
            return False, "Products data must be a list"
        
        required_fields = ['id', 'title', 'price', 'category']
        
        for i, product in enumerate(products):
            for field in required_fields:
                if field not in product:
                    return False, f"Product {i} missing field: {field}"
            
            # Validate data types
            if not isinstance(product['price'], (int, float)):
                return False, f"Product {i} has invalid price type"
        
        return True, f"Validated {len(products)} products"
    
    except Exception as e:
        return False, f"Validation error: {e}"

# Run validation
is_valid, message = validate_products_data('html/JS/productos.json')
print(f"Validation result: {message}")
```

## System Restoration

### Complete System Restoration

#### From Backup
```bash
#!/bin/bash
# complete_restore.sh

echo "Starting complete system restoration..."

# 1. Create restoration point
RESTORE_POINT="restore_$(date +%Y%m%d_%H%M%S)"
mkdir -p "restore_points/$RESTORE_POINT"
cp -r html "restore_points/$RESTORE_POINT/"
cp *.py "restore_points/$RESTORE_POINT/"

# 2. Stop all services
echo "Stopping services..."
# Add service stop commands here

# 3. Restore from backup
BACKUP_DIR="backups/backup_20231201_120000"  # Specify backup
echo "Restoring from $BACKUP_DIR..."

cp -r "$BACKUP_DIR/html" ./
cp "$BACKUP_DIR"/*.py ./
cp -r "$BACKUP_DIR/Programa" ./

# 4. Restore Git repository
if [ -d "$BACKUP_DIR/.git" ]; then
    cp -r "$BACKUP_DIR/.git" ./
fi

# 5. Validate restoration
echo "Validating restoration..."
python -c "import json; json.load(open('html/JS/productos.json'))"

if [ $? -eq 0 ]; then
    echo "✅ System restoration completed successfully"
else
    echo "❌ System restoration failed - rolling back"
    cp -r "restore_points/$RESTORE_POINT/"* ./
    exit 1
fi

# 6. Start services
echo "Starting services..."
# Add service start commands here

echo "🎉 Complete system restoration finished"
```

### Environment Rebuild

#### Development Environment
```bash
# 1. Clean environment
rm -rf venv/
rm -rf __pycache__/
rm -rf *.pyc

# 2. Recreate virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Restore data
cp backups/latest_backup.json html/JS/productos.json

# 5. Test environment
python customtk.py
```

#### Production Environment
```bash
# 1. Prepare new environment
mkdir deportes_guemes_new
cd deportes_guemes_new

# 2. Clone repository
git clone <repository-url> .

# 3. Restore data from backup
cp ../backups/latest_backup.json html/JS/productos.json

# 4. Configure environment
cp ../deploy-config.json ./

# 5. Deploy
python scripts/deploy.py deploy --environment production

# 6. Switch traffic to new environment
# (Update DNS, load balancer, etc.)
```

## Communication Protocols

### Internal Communication

#### Incident Notification Template
```
INCIDENT ALERT - [SEVERITY LEVEL]

Incident ID: INC-YYYYMMDD-001
Time: [Timestamp]
Severity: [P0/P1/P2/P3]
System: Deportes Güemes [Desktop/Web/Both]

IMPACT:
- Affected Users: [Number/All/Specific group]
- Business Impact: [High/Medium/Low]
- Services Down: [List affected services]

CURRENT STATUS:
- Detection Time: [Timestamp]
- Response Team: [Names]
- Initial Assessment: [Brief description]
- ETA for Resolution: [Estimate]

ACTIONS TAKEN:
- [List immediate actions]

NEXT STEPS:
- [Planned actions]

Updates will be provided every 30 minutes.
```

### External Communication

#### Customer Notification Template
```
Service Update - Deportes Güemes

We are currently experiencing technical difficulties with our [web store/desktop application]. 

Impact: [Brief description of what customers might experience]
Estimated Resolution: [Time estimate]

We apologize for any inconvenience and are working to resolve this as quickly as possible.

Updates: [Where customers can get updates]
Support: [Contact information for urgent issues]

Thank you for your patience.
```

### Communication Channels

#### Internal
- **Slack/Teams**: Real-time team communication
- **Email**: Formal notifications and updates
- **Phone**: Critical escalations
- **Incident Management Tool**: Ticket tracking

#### External
- **Website Banner**: Service status notifications
- **Email**: Customer notifications
- **Social Media**: Public updates if needed
- **Support System**: Individual customer responses

## Post-Incident Analysis

### Incident Review Process

#### Within 24 Hours
1. **Immediate Review Meeting**
   - What happened?
   - Timeline of events
   - Response effectiveness
   - Immediate lessons learned

#### Within 1 Week
2. **Detailed Post-Mortem**
   - Root cause analysis
   - Contributing factors
   - Response evaluation
   - Action items identification

### Post-Mortem Template

```markdown
# Post-Incident Review: [Incident ID]

## Incident Summary
- **Date/Time**: [When incident occurred]
- **Duration**: [How long it lasted]
- **Severity**: [P0/P1/P2/P3]
- **Impact**: [Business and user impact]

## Timeline
| Time | Event | Action Taken |
|------|-------|--------------|
| 14:30 | Issue detected | Monitoring alert triggered |
| 14:35 | Team notified | Incident response activated |
| 14:45 | Root cause identified | Rollback initiated |
| 15:00 | Service restored | Verification completed |

## Root Cause Analysis
### Primary Cause
[Detailed explanation of what caused the incident]

### Contributing Factors
- [Factor 1]
- [Factor 2]
- [Factor 3]

## What Went Well
- [Positive aspects of response]
- [Effective procedures]
- [Good decisions made]

## What Could Be Improved
- [Areas for improvement]
- [Process gaps identified]
- [Response delays]

## Action Items
| Action | Owner | Due Date | Priority |
|--------|-------|----------|----------|
| Improve monitoring | Tech Lead | Next week | High |
| Update procedures | SysAdmin | 2 weeks | Medium |
| Training session | Team | 1 month | Low |

## Prevention Measures
- [How to prevent similar incidents]
- [Process improvements]
- [Technical improvements]
```

## Prevention Measures

### Proactive Monitoring

#### System Health Checks
```bash
#!/bin/bash
# health_check.sh - Run every 5 minutes

# Check web store accessibility
curl -f http://localhost:8000/html/index.html > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ALERT: Web store not accessible" | mail -s "Health Check Alert" admin@company.com
fi

# Check JSON data integrity
python -c "import json; json.load(open('html/JS/productos.json'))" > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "ALERT: Products data corrupted" | mail -s "Data Integrity Alert" admin@company.com
fi

# Check disk space
DISK_USAGE=$(df / | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 90 ]; then
    echo "ALERT: Disk usage at ${DISK_USAGE}%" | mail -s "Disk Space Alert" admin@company.com
fi
```

#### Automated Backups
```bash
#!/bin/bash
# automated_backup.sh - Run daily

DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="backups/auto_backup_$DATE"

mkdir -p "$BACKUP_DIR"

# Backup data files
cp html/JS/productos.json "$BACKUP_DIR/"
cp html/JS/historial.json "$BACKUP_DIR/"

# Backup images
cp -r html/img "$BACKUP_DIR/"

# Backup Python files
cp *.py "$BACKUP_DIR/"
cp -r Programa "$BACKUP_DIR/"

# Create backup info
echo "{
    \"timestamp\": \"$DATE\",
    \"type\": \"automated\",
    \"files\": $(find "$BACKUP_DIR" -type f | wc -l),
    \"size\": $(du -sb "$BACKUP_DIR" | cut -f1)
}" > "$BACKUP_DIR/backup_info.json"

# Clean old backups (keep last 30 days)
find backups/ -name "auto_backup_*" -mtime +30 -exec rm -rf {} \;

echo "Automated backup completed: $BACKUP_DIR"
```

### Testing Procedures

#### Regular Disaster Recovery Tests
```bash
#!/bin/bash
# dr_test.sh - Run monthly

echo "Starting Disaster Recovery Test..."

# 1. Create test environment
TEST_DIR="dr_test_$(date +%Y%m%d)"
mkdir "$TEST_DIR"
cd "$TEST_DIR"

# 2. Simulate data loss
echo "Simulating data loss scenario..."

# 3. Test backup restoration
echo "Testing backup restoration..."
cp ../backups/latest_backup.json productos.json

# 4. Validate restoration
python -c "import json; data=json.load(open('productos.json')); print(f'Restored {len(data)} products')"

# 5. Test application startup
echo "Testing application startup..."
# Add application tests here

# 6. Cleanup
cd ..
rm -rf "$TEST_DIR"

echo "✅ Disaster Recovery Test Completed"
```

### Documentation Maintenance

#### Regular Updates Required
- [ ] Emergency contact information
- [ ] Backup locations and procedures
- [ ] System dependencies and versions
- [ ] Recovery time objectives (RTO)
- [ ] Recovery point objectives (RPO)
- [ ] Escalation procedures

#### Training Schedule
- **Monthly**: Team review of procedures
- **Quarterly**: Disaster recovery drill
- **Annually**: Full emergency response training
- **As needed**: New team member onboarding

---

## Emergency Checklist Quick Reference

### Critical Incident (P0) Response
- [ ] Notify Incident Commander immediately
- [ ] Activate emergency response team
- [ ] Create incident war room
- [ ] Begin incident documentation
- [ ] Assess rollback necessity
- [ ] Communicate with stakeholders
- [ ] Execute recovery procedures
- [ ] Verify system restoration
- [ ] Conduct post-incident review

### Rollback Decision Matrix
| Condition | Action |
|-----------|--------|
| Data corruption detected | Immediate rollback |
| Complete system failure | Immediate rollback |
| Performance degradation >50% | Consider rollback |
| Minor functionality issues | Fix forward |
| Cosmetic issues only | Fix forward |

### Recovery Time Objectives
- **Critical Systems**: 15 minutes
- **Major Features**: 1 hour
- **Minor Features**: 4 hours
- **Cosmetic Issues**: 24 hours

---

*Last updated: [Current Date]*
*Document version: 1.0.0*
*Next review date: [Date + 3 months]*