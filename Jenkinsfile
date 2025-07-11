// Jenkinsfile - pipeline build
pipeline {
    agent any
    
    // Step 1a-c. Triggers
    // These are the essential triggers, no others as would result in unnecessary runs - competing with step 1
    triggers {
        // Poll SCM every 5 minutes for changes
        pollSCM('H/5 * * * *')
        // Trigger build on each Github push
        githubPush()
    }
    
    environment {
        PYTHONPATH = "${WORKSPACE}"
        COVERAGE_MIN = '60'
    }
    // Step 2a. Checkout source code from repository
    stages {
        stage('Initialization') {
            steps {
                echo 'Building.. checking out source code'
                checkout scm
                
                script {
                    echo "Build Number: ${env.BUILD_NUMBER}"
                    echo "Branch: ${env.BRANCH_NAME ?: 'main'}"
                }
            }
        }
        
        // Step 2b. Install and configure correct runtime environment
        // Step 2c. Install project dependencies on appropriate package managers
        // Step 2d. Setup required environment variables and config files
        stage('Setup Environment') {
            steps {
                echo 'Building.. setting up Python environment'
                
                bat '''
                    if exist "venv" rmdir /s /q venv
                    C:\\Users\\Carte\\AppData\\Local\\Programs\\Python\\Python313\\python.exe -m venv venv
                    call venv\\Scripts\\activate.bat
                    pip install -r requirements.txt
                    pip install ruff black coverage pytest pytest-cov
                '''
            }
        }
        
        // 3a. Configure and run Ruff linting
        stage('Code Quality') {
            steps {
                echo 'Code Quality.. running Ruff Linting'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    ruff check . --output-format=full > ruff-report.txt 2>&1 || exit /b 0
                    type ruff-report.txt
                '''
                
                
                // 3c. Configure quality gates if standards aren't met
                script {
                    def lintResult = bat(
                        script: '''
                            call venv\\Scripts\\activate.bat
                            ruff check . --quiet
                        ''',
                        returnStatus: true
                    )
                    
                    archiveArtifacts artifacts: 'ruff-report.txt', allowEmptyArchive: true
                    
                    if (lintResult != 0) {
                        error("Linting failed. Please fix the issues reported by Ruff.")
                    }
                }
            }
        }
        
        // 3b. Implement code formatting check tool for Black
        stage('Code Quality - Formatting') {
            steps {
        echo 'Code Quality.. fixing formatting with Black.'
        
        script {
            def formatResult = bat(
                script: '''
                    call venv\\Scripts\\activate.bat
                    black --color . > black-report.txt 2>&1
                    exit /b %ERRORLEVEL%
                ''',
                returnStatus: true
            )
            
            // 3c. Configure quality gates if standards aren't met
            archiveArtifacts artifacts: 'black-report.txt', allowEmptyArchive: true 
            
            if (formatResult != 0) {
                bat 'type black-report.txt'

                error("Black attempted to fix formatting issues, but encountered an error. Check 'black-report.txt' for details.")
            } else {
                echo "Code formatting fixed or already correct."
                }
            }
        }
    }
        
        // 4a. Execute all unit tests with appropriate testing framework
        stage('Testing') {
            steps {
                echo 'Testing.. running unit tests with coverage...'
                bat '''
                    call venv\\Scripts\\activate.bat
                    
                    REM Run tests with coverage and generate JUnit XML
                    coverage run -m pytest test_app.py -v --junitxml=test-results.xml
                    
                    REM Generate coverage reports (text, HTML, and Cobertura XML)
                    coverage report --fail-under=%COVERAGE_MIN%
                    coverage html --directory=htmlcov
                    coverage xml
                '''
            }
            
            // 4b. Generate comprehensive test coverage reports (post-stage actions)
            post {
                always {
                    // Publish JUnit test results for analysis in Jenkins UI
                    junit(
                        testResults: 'test-results.xml',
                        allowEmptyResults: true    
                    )
                    
                    archiveArtifacts artifacts: 'test-results.xml,coverage.xml,htmlcov/**/*', allowEmptyArchive: true
                }
            }
        }

        
        // 5a. Compile and build the application
        stage('Build Application') {
            steps {
                echo 'Building Flask application...'
                
                bat '''
                    call venv\\Scripts\\activate.bat
                    python -c "from app import app; print('Flask app imports successfully')"
                    python -c "from app import init_db; init_db(); print('Database initializes successfully')"
                    
                    echo Build Number: %BUILD_NUMBER% > build-info.txt
                    echo Build Date: %DATE% %TIME% >> build-info.txt
                    echo Branch: %BRANCH_NAME% >> build-info.txt
                '''
            }
        }
        
        // 5b. Verify that all build artifacts are successfully generated
        stage('Verify Build Artifacts') {
            steps {
                echo 'Verifying build artifacts...'
                
                bat '''
                    if not exist "app.py" exit /b 1
                    if not exist "requirements.txt" exit /b 1
                    if not exist "templates" exit /b 1
                    
                    echo All required files present
                    type build-info.txt
                '''
                
                archiveArtifacts artifacts: 'build-info.txt', allowEmptyArchive: true
            }
        }
    }
    
    // Post-build actions
    post {
        always {
            // Clean up workspace
            echo 'Cleaning up workspace'

            // Clean up virtual environment
            bat '''
                if exist "venv" rmdir /s /q venv
            '''
        }

        success {
            // Pipeline completed successfully
            echo 'Pipeline successful!'

            // Publish test results
            junit(
                testResults: 'test-results.xml',
                allowEmptyResults: true
            )

            // Archive test artifacts
            archiveArtifacts artifacts: 'test-results.xml,coverage.xml,htmlcov/**/*', allowEmptyArchive: true
        }

        failure {
            // Pipeline failed
            echo 'Pipeline failed!'

            // Publish test results
            junit(
                testResults: 'test-results.xml',
                allowEmptyResults: true
            )
            // Archive test artifacts
            archiveArtifacts artifacts: 'test-results.xml,coverage.xml,htmlcov/**/*', allowEmptyArchive: true
        }

        unstable {
            // Build is unstable
            echo 'Build unstable!'
            // Publish test results
            junit(
                testResults: 'test-results.xml',
                allowEmptyResults: true
            )
            // Archive test artifacts
            archiveArtifacts artifacts: 'test-results.xml,coverage.xml,htmlcov/**/*', allowEmptyArchive: true
        }
    }
}